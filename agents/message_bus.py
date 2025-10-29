"""
Message Bus for Agent-to-Agent (A2A) Communication
Implements async message passing with routing, priority queues, and delivery guarantees
"""

import asyncio
import logging
from typing import Dict, List, Callable, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict
import json


@dataclass
class MessageAcknowledgment:
    """Acknowledgment of message receipt"""
    message_id: str
    recipient_id: str
    timestamp: str
    status: str  # received, processed, failed


class MessageBus:
    """
    Central message bus for agent-to-agent communication
    Features:
    - Priority-based message queuing
    - Message routing and delivery
    - At-least-once delivery with acknowledgments
    - Message history and audit trail
    - Dead letter queue for failed messages
    """

    def __init__(self, logger: Optional[logging.Logger] = None):
        """Initialize message bus"""
        self.logger = logger or self._setup_logger()

        # Message queues by priority
        self.queues: Dict[str, asyncio.Queue] = {
            "critical": asyncio.Queue(),
            "high": asyncio.Queue(),
            "normal": asyncio.Queue(),
            "low": asyncio.Queue()
        }

        # Subscriber registry: agent_id -> list of callback functions
        self.subscribers: Dict[str, List[Callable]] = defaultdict(list)

        # Message tracking
        self.pending_messages: Dict[str, Any] = {}  # message_id -> message
        self.acknowledged_messages: Dict[str, MessageAcknowledgment] = {}
        self.failed_messages: List[Any] = []  # Dead letter queue
        self.message_history: List[Dict[str, Any]] = []

        # Configuration
        self.max_delivery_attempts = 3
        self.acknowledgment_timeout_seconds = 30
        self.running = False

        self.logger.info("Message bus initialized")

    def _setup_logger(self) -> logging.Logger:
        """Setup default logger"""
        logger = logging.getLogger("MessageBus")
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    async def start(self):
        """Start message bus processing"""
        if self.running:
            self.logger.warning("Message bus already running")
            return

        self.running = True
        self.logger.info("Message bus started")

        # Start processing tasks for each priority queue
        tasks = [
            asyncio.create_task(self._process_queue("critical")),
            asyncio.create_task(self._process_queue("high")),
            asyncio.create_task(self._process_queue("normal")),
            asyncio.create_task(self._process_queue("low")),
            asyncio.create_task(self._cleanup_expired_messages())
        ]

        await asyncio.gather(*tasks, return_exceptions=True)

    async def stop(self):
        """Stop message bus processing"""
        self.running = False
        self.logger.info("Message bus stopped")

    async def _process_queue(self, priority: str):
        """Process messages from a specific priority queue"""
        queue = self.queues[priority]

        while self.running:
            try:
                # Get message from queue (wait up to 1 second)
                try:
                    message = await asyncio.wait_for(queue.get(), timeout=1.0)
                except asyncio.TimeoutError:
                    continue

                self.logger.debug(f"Processing {priority} priority message: {message.message_id}")

                # Route message to recipient(s)
                await self._route_message(message)

                # Mark task as done
                queue.task_done()

            except Exception as e:
                self.logger.error(f"Error processing {priority} queue: {str(e)}")
                await asyncio.sleep(1)

    async def _route_message(self, message: Any):
        """Route message to appropriate recipient(s)"""
        recipient_id = message.recipient_id

        # Track message
        self.pending_messages[message.message_id] = {
            "message": message,
            "attempts": 0,
            "first_attempt": datetime.now().isoformat(),
            "last_attempt": None
        }

        # Get subscribers for recipient
        callbacks = self.subscribers.get(recipient_id, [])

        if not callbacks:
            self.logger.warning(f"No subscribers for recipient {recipient_id}")
            self._move_to_dead_letter(message, "No subscribers")
            return

        # Deliver to all subscribers
        delivery_successful = False
        for callback in callbacks:
            try:
                await callback(message)
                delivery_successful = True
                self.logger.debug(f"Message {message.message_id} delivered to {recipient_id}")
            except Exception as e:
                self.logger.error(
                    f"Error delivering message {message.message_id} to {recipient_id}: {str(e)}"
                )

        if delivery_successful:
            # Update tracking
            self.pending_messages[message.message_id]["attempts"] += 1
            self.pending_messages[message.message_id]["last_attempt"] = datetime.now().isoformat()

            # Record in history
            self.message_history.append({
                "message_id": message.message_id,
                "sender_id": message.sender_id,
                "recipient_id": message.recipient_id,
                "message_type": message.message_type,
                "priority": message.priority,
                "timestamp": message.timestamp,
                "delivered_at": datetime.now().isoformat()
            })
        else:
            # Retry or move to dead letter queue
            attempts = self.pending_messages[message.message_id]["attempts"] + 1
            if attempts < self.max_delivery_attempts:
                self.logger.info(f"Retrying message {message.message_id} (attempt {attempts})")
                await self.publish(message)  # Re-queue
            else:
                self._move_to_dead_letter(message, "Max delivery attempts exceeded")

    async def publish(self, message: Any):
        """
        Publish message to bus

        Args:
            message: AgentMessage to publish
        """
        priority = message.priority
        queue = self.queues.get(priority, self.queues["normal"])

        await queue.put(message)
        self.logger.debug(f"Message {message.message_id} published with priority {priority}")

    def subscribe(self, agent_id: str, callback: Callable):
        """
        Subscribe agent to receive messages

        Args:
            agent_id: Agent identifier
            callback: Async function to call when message received
        """
        self.subscribers[agent_id].append(callback)
        self.logger.info(f"Agent {agent_id} subscribed to message bus")

    def unsubscribe(self, agent_id: str, callback: Optional[Callable] = None):
        """
        Unsubscribe agent from messages

        Args:
            agent_id: Agent identifier
            callback: Specific callback to remove (removes all if None)
        """
        if callback:
            if callback in self.subscribers[agent_id]:
                self.subscribers[agent_id].remove(callback)
        else:
            self.subscribers[agent_id] = []

        self.logger.info(f"Agent {agent_id} unsubscribed from message bus")

    async def acknowledge(self, message_id: str, recipient_id: str, status: str = "processed"):
        """
        Acknowledge message receipt/processing

        Args:
            message_id: Message to acknowledge
            recipient_id: Agent acknowledging
            status: Acknowledgment status (received, processed, failed)
        """
        ack = MessageAcknowledgment(
            message_id=message_id,
            recipient_id=recipient_id,
            timestamp=datetime.now().isoformat(),
            status=status
        )

        self.acknowledged_messages[message_id] = ack

        # Remove from pending if processed
        if status == "processed" and message_id in self.pending_messages:
            del self.pending_messages[message_id]

        self.logger.debug(f"Message {message_id} acknowledged by {recipient_id} with status {status}")

    async def _cleanup_expired_messages(self):
        """Cleanup messages that haven't been acknowledged within timeout"""
        while self.running:
            try:
                await asyncio.sleep(10)  # Check every 10 seconds

                now = datetime.now()
                expired = []

                for message_id, tracking in self.pending_messages.items():
                    first_attempt = datetime.fromisoformat(tracking["first_attempt"])
                    age = (now - first_attempt).total_seconds()

                    if age > self.acknowledgment_timeout_seconds:
                        expired.append(message_id)

                # Move expired messages to dead letter queue
                for message_id in expired:
                    tracking = self.pending_messages[message_id]
                    self._move_to_dead_letter(
                        tracking["message"],
                        f"Acknowledgment timeout ({self.acknowledgment_timeout_seconds}s)"
                    )
                    del self.pending_messages[message_id]

            except Exception as e:
                self.logger.error(f"Error in cleanup task: {str(e)}")

    def _move_to_dead_letter(self, message: Any, reason: str):
        """Move message to dead letter queue"""
        self.failed_messages.append({
            "message": message,
            "reason": reason,
            "timestamp": datetime.now().isoformat()
        })

        self.logger.warning(
            f"Message {message.message_id} moved to dead letter queue: {reason}"
        )

    def get_statistics(self) -> Dict[str, Any]:
        """Get message bus statistics"""
        return {
            "running": self.running,
            "queue_sizes": {
                priority: queue.qsize()
                for priority, queue in self.queues.items()
            },
            "subscribers_count": len(self.subscribers),
            "pending_messages": len(self.pending_messages),
            "acknowledged_messages": len(self.acknowledged_messages),
            "failed_messages": len(self.failed_messages),
            "total_messages_processed": len(self.message_history)
        }

    def get_agent_message_history(self, agent_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get message history for specific agent"""
        agent_messages = [
            msg for msg in self.message_history
            if msg["sender_id"] == agent_id or msg["recipient_id"] == agent_id
        ]

        return agent_messages[-limit:]

    def get_dead_letter_messages(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get failed messages from dead letter queue"""
        if limit:
            return self.failed_messages[-limit:]
        return self.failed_messages

    def clear_dead_letter_queue(self):
        """Clear dead letter queue"""
        count = len(self.failed_messages)
        self.failed_messages = []
        self.logger.info(f"Cleared {count} messages from dead letter queue")


class MessageRouter:
    """
    Advanced message routing with load balancing
    Routes messages to appropriate agents based on capabilities and load
    """

    def __init__(self, message_bus: MessageBus, logger: Optional[logging.Logger] = None):
        """Initialize router"""
        self.message_bus = message_bus
        self.logger = logger or logging.getLogger("MessageRouter")

        # Agent registry: agent_type -> list of agent_ids
        self.agent_registry: Dict[str, List[str]] = defaultdict(list)

        # Agent capabilities: agent_id -> capabilities dict
        self.agent_capabilities: Dict[str, Dict[str, Any]] = {}

        # Agent load tracking: agent_id -> current task count
        self.agent_load: Dict[str, int] = defaultdict(int)

    def register_agent(self, agent_id: str, agent_type: str, capabilities: Dict[str, Any]):
        """Register agent with router"""
        self.agent_registry[agent_type].append(agent_id)
        self.agent_capabilities[agent_id] = capabilities
        self.agent_load[agent_id] = 0

        self.logger.info(f"Registered agent {agent_id} of type {agent_type}")

    def unregister_agent(self, agent_id: str, agent_type: str):
        """Unregister agent from router"""
        if agent_id in self.agent_registry[agent_type]:
            self.agent_registry[agent_type].remove(agent_id)

        if agent_id in self.agent_capabilities:
            del self.agent_capabilities[agent_id]

        if agent_id in self.agent_load:
            del self.agent_load[agent_id]

        self.logger.info(f"Unregistered agent {agent_id}")

    def select_agent(
        self,
        agent_type: str,
        required_capabilities: Optional[List[str]] = None,
        load_balance: bool = True
    ) -> Optional[str]:
        """
        Select best agent for task

        Args:
            agent_type: Type of agent needed
            required_capabilities: List of required capabilities
            load_balance: Whether to consider agent load

        Returns:
            agent_id of selected agent, or None if none available
        """
        candidates = self.agent_registry.get(agent_type, [])

        if not candidates:
            return None

        # Filter by capabilities if specified
        if required_capabilities:
            candidates = [
                agent_id for agent_id in candidates
                if all(
                    cap in self.agent_capabilities.get(agent_id, {}).get("capabilities", [])
                    for cap in required_capabilities
                )
            ]

        if not candidates:
            return None

        # Load balancing: select agent with lowest current load
        if load_balance:
            selected = min(candidates, key=lambda a: self.agent_load[a])
        else:
            selected = candidates[0]

        return selected

    def increment_agent_load(self, agent_id: str):
        """Increment agent's current load"""
        self.agent_load[agent_id] += 1

    def decrement_agent_load(self, agent_id: str):
        """Decrement agent's current load"""
        if self.agent_load[agent_id] > 0:
            self.agent_load[agent_id] -= 1

    def get_agent_load_stats(self) -> Dict[str, Any]:
        """Get load statistics across all agents"""
        if not self.agent_load:
            return {"total_agents": 0, "total_load": 0, "average_load": 0.0}

        total_load = sum(self.agent_load.values())
        average_load = total_load / len(self.agent_load)

        return {
            "total_agents": len(self.agent_load),
            "total_load": total_load,
            "average_load": average_load,
            "agent_loads": dict(self.agent_load)
        }
