#!/usr/bin/env python3
"""
ROS (Robot Operating System) Integration Adapter

Provides ROS-specific integration for the distributed cognitive mesh.
Handles bidirectional communication with ROS nodes for robotic embodied cognition.

Key Features:
- ROS message publishing and subscription
- Service client/server communication
- Action server integration
- Real-time sensor data streaming
- Motor control and actuation
- Transformation and navigation support
"""

import json
import time
import threading
import numpy as np
from typing import Dict, List, Any, Optional, Tuple, Callable
from dataclasses import dataclass, asdict
import logging
from concurrent.futures import ThreadPoolExecutor
import socket
import struct

logger = logging.getLogger(__name__)


@dataclass
class ROSMessage:
    """Represents a ROS message"""
    topic: str
    message_type: str
    data: Dict[str, Any]
    timestamp: float = 0.0
    frame_id: str = ""

    def __post_init__(self):
        if self.timestamp == 0.0:
            self.timestamp = time.time()


@dataclass
class ROSService:
    """Represents a ROS service"""
    service_name: str
    service_type: str
    callback: Callable
    active: bool = True


@dataclass
class ROSAction:
    """Represents a ROS action"""
    action_name: str
    action_type: str
    goal: Dict[str, Any]
    status: str = "pending"  # pending, active, succeeded, failed, cancelled
    feedback: Dict[str, Any] = None
    result: Dict[str, Any] = None
    action_id: str = ""

    def __post_init__(self):
        if self.feedback is None:
            self.feedback = {}
        if self.result is None:
            self.result = {}
        if not self.action_id:
            self.action_id = f"action_{int(time.time() * 1000)}"


@dataclass
class ROSCognitiveAgent:
    """Represents a cognitive agent embodied in ROS"""
    agent_id: str
    node_name: str
    robot_type: str  # "mobile_robot", "manipulator", "humanoid", etc.
    pose: Dict[str, Any]  # position and orientation
    joint_states: Dict[str, float]
    sensor_data: Dict[str, Any]
    actuator_states: Dict[str, Any]
    cognitive_state: Dict[str, Any]
    capabilities: List[str]
    last_update: float = 0.0

    def __post_init__(self):
        if self.last_update == 0.0:
            self.last_update = time.time()


class ROSMessageTypes:
    """Common ROS message type definitions"""
    
    # Standard messages
    STD_MSGS_STRING = "std_msgs/String"
    STD_MSGS_FLOAT32 = "std_msgs/Float32"
    STD_MSGS_FLOAT64 = "std_msgs/Float64"
    STD_MSGS_INT32 = "std_msgs/Int32"
    STD_MSGS_BOOL = "std_msgs/Bool"
    
    # Geometry messages
    GEOMETRY_MSGS_POINT = "geometry_msgs/Point"
    GEOMETRY_MSGS_POSE = "geometry_msgs/Pose"
    GEOMETRY_MSGS_POSE_STAMPED = "geometry_msgs/PoseStamped"
    GEOMETRY_MSGS_TWIST = "geometry_msgs/Twist"
    GEOMETRY_MSGS_TRANSFORM = "geometry_msgs/Transform"
    
    # Sensor messages
    SENSOR_MSGS_IMAGE = "sensor_msgs/Image"
    SENSOR_MSGS_POINT_CLOUD = "sensor_msgs/PointCloud2"
    SENSOR_MSGS_LASER_SCAN = "sensor_msgs/LaserScan"
    SENSOR_MSGS_IMU = "sensor_msgs/Imu"
    SENSOR_MSGS_JOINT_STATE = "sensor_msgs/JointState"
    
    # Navigation messages
    NAV_MSGS_ODOMETRY = "nav_msgs/Odometry"
    NAV_MSGS_OCCUPANCY_GRID = "nav_msgs/OccupancyGrid"
    
    # Action messages
    MOVE_BASE_ACTION = "move_base_msgs/MoveBaseAction"
    FOLLOW_JOINT_TRAJECTORY = "control_msgs/FollowJointTrajectoryAction"


class ROSProtocol:
    """Protocol handler for ROS communication"""
    
    # Message types for our custom protocol
    MSG_PUBLISH = 0x10
    MSG_SUBSCRIBE = 0x11
    MSG_SERVICE_CALL = 0x12
    MSG_SERVICE_RESPONSE = 0x13
    MSG_ACTION_GOAL = 0x14
    MSG_ACTION_FEEDBACK = 0x15
    MSG_ACTION_RESULT = 0x16
    MSG_AGENT_STATE = 0x17
    MSG_COGNITIVE_UPDATE = 0x18
    MSG_HEARTBEAT = 0x19
    
    @staticmethod
    def pack_message(msg_type: int, data: Dict[str, Any]) -> bytes:
        """Pack a message for ROS transmission"""
        json_data = json.dumps(data, default=str).encode('utf-8')
        header = struct.pack('!BI', msg_type, len(json_data))
        return header + json_data
    
    @staticmethod
    def unpack_message(data: bytes) -> Tuple[int, Dict[str, Any]]:
        """Unpack a message from ROS"""
        if len(data) < 5:
            raise ValueError("Message too short")
        
        msg_type, data_length = struct.unpack('!BI', data[:5])
        json_data = data[5:5+data_length].decode('utf-8')
        
        return msg_type, json.loads(json_data)


class ROSIntegrationAdapter:
    """Main adapter for ROS embodiment integration"""
    
    def __init__(self, port: int = 8888, ros_master_uri: str = "http://localhost:11311", bind_address: str = "127.0.0.1"):
        self.port = port
        self.ros_master_uri = ros_master_uri
        self.bind_address = bind_address
        
        # Connection management
        self.server_socket = None
        self.client_connections: Dict[str, socket.socket] = {}
        self.connection_threads: Dict[str, threading.Thread] = {}
        
        # ROS component tracking
        self.published_topics: Dict[str, ROSMessage] = {}
        self.subscribed_topics: Dict[str, List[Callable]] = {}
        self.active_services: Dict[str, ROSService] = {}
        self.active_actions: Dict[str, ROSAction] = {}
        
        # Agent management
        self.ros_agents: Dict[str, ROSCognitiveAgent] = {}
        
        # Message queues
        self.outgoing_messages = []
        self.incoming_messages = []
        
        # ROS system state
        self.ros_system_state = {
            "master_uri": ros_master_uri,
            "active_nodes": [],
            "available_topics": [],
            "available_services": [],
            "tf_tree": {}
        }
        
        self.running = False
        self.executor = ThreadPoolExecutor(max_workers=20)
        
        logger.info("ROS Integration Adapter initialized")
    
    def start_server(self):
        """Start the ROS integration server"""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.bind_address, self.port))
        self.server_socket.listen(5)
        
        self.running = True
        
        # Start connection acceptor thread
        threading.Thread(target=self._accept_connections, daemon=True).start()
        
        # Start message processor thread
        threading.Thread(target=self._process_messages, daemon=True).start()
        
        # Start ROS system monitor
        threading.Thread(target=self._monitor_ros_system, daemon=True).start()
        
        logger.info(f"ROS server started on port {self.port}")
    
    def stop_server(self):
        """Stop the ROS integration server"""
        self.running = False
        
        # Close all client connections
        for conn_id, conn in self.client_connections.items():
            try:
                conn.close()
            except:
                pass
        
        # Close server socket
        if self.server_socket:
            self.server_socket.close()
        
        logger.info("ROS server stopped")
    
    def _accept_connections(self):
        """Accept incoming ROS node connections"""
        while self.running:
            try:
                client_socket, address = self.server_socket.accept()
                connection_id = f"ros_{address[0]}_{address[1]}_{int(time.time())}"
                
                self.client_connections[connection_id] = client_socket
                
                # Start handler thread for this connection
                handler_thread = threading.Thread(
                    target=self._handle_ros_client,
                    args=(connection_id, client_socket),
                    daemon=True
                )
                handler_thread.start()
                self.connection_threads[connection_id] = handler_thread
                
                logger.info(f"New ROS connection: {connection_id} from {address}")
                
                # Send handshake
                handshake_msg = ROSProtocol.pack_message(
                    ROSProtocol.MSG_HEARTBEAT,
                    {
                        "connection_id": connection_id,
                        "server_version": "1.0.0",
                        "ros_master_uri": self.ros_master_uri,
                        "capabilities": [
                            "topic_publishing",
                            "topic_subscription",
                            "service_calls",
                            "action_execution",
                            "cognitive_integration"
                        ],
                        "timestamp": time.time()
                    }
                )
                client_socket.send(handshake_msg)
                
            except Exception as e:
                if self.running:
                    logger.error(f"ROS connection accept error: {str(e)}")
                break
    
    def _handle_ros_client(self, connection_id: str, client_socket: socket.socket):
        """Handle communication with a ROS client"""
        buffer = b""
        
        while self.running:
            try:
                data = client_socket.recv(4096)
                if not data:
                    break
                
                buffer += data
                
                # Process complete messages in buffer
                while len(buffer) >= 5:
                    try:
                        msg_type, data_length = struct.unpack('!BI', buffer[:5])
                        total_length = 5 + data_length
                        
                        if len(buffer) < total_length:
                            break
                        
                        message_data = buffer[:total_length]
                        buffer = buffer[total_length:]
                        
                        self._process_ros_message(connection_id, message_data)
                        
                    except Exception as e:
                        logger.error(f"ROS message processing error: {str(e)}")
                        break
                
            except Exception as e:
                logger.error(f"ROS client handling error: {str(e)}")
                break
        
        self._cleanup_ros_connection(connection_id)
    
    def _process_ros_message(self, connection_id: str, message_data: bytes):
        """Process a message from ROS"""
        try:
            msg_type, data = ROSProtocol.unpack_message(message_data)
            
            if msg_type == ROSProtocol.MSG_PUBLISH:
                self._handle_topic_publish(connection_id, data)
            elif msg_type == ROSProtocol.MSG_SUBSCRIBE:
                self._handle_topic_subscribe(connection_id, data)
            elif msg_type == ROSProtocol.MSG_SERVICE_CALL:
                self._handle_service_call(connection_id, data)
            elif msg_type == ROSProtocol.MSG_ACTION_GOAL:
                self._handle_action_goal(connection_id, data)
            elif msg_type == ROSProtocol.MSG_AGENT_STATE:
                self._handle_agent_state_update(connection_id, data)
            elif msg_type == ROSProtocol.MSG_HEARTBEAT:
                self._handle_ros_heartbeat(connection_id, data)
            else:
                logger.warning(f"Unknown ROS message type: {msg_type}")
                
        except Exception as e:
            logger.error(f"ROS message processing error: {str(e)}")
    
    def _handle_topic_publish(self, connection_id: str, data: Dict[str, Any]):
        """Handle topic publication from ROS"""
        topic = data.get('topic')
        message_type = data.get('message_type')
        message_data = data.get('data', {})
        
        ros_message = ROSMessage(
            topic=topic,
            message_type=message_type,
            data=message_data,
            frame_id=data.get('frame_id', '')
        )
        
        self.published_topics[topic] = ros_message
        
        # Notify subscribers
        if topic in self.subscribed_topics:
            for callback in self.subscribed_topics[topic]:
                try:
                    callback(ros_message)
                except Exception as e:
                    logger.error(f"Subscription callback error: {str(e)}")
        
        logger.debug(f"Published to topic: {topic}")
    
    def _handle_topic_subscribe(self, connection_id: str, data: Dict[str, Any]):
        """Handle topic subscription from ROS"""
        topic = data.get('topic')
        
        if topic not in self.subscribed_topics:
            self.subscribed_topics[topic] = []
        
        # Add callback for this connection
        def connection_callback(message: ROSMessage):
            self._forward_message_to_connection(connection_id, message)
        
        self.subscribed_topics[topic].append(connection_callback)
        
        logger.debug(f"Subscribed to topic: {topic}")
    
    def _handle_service_call(self, connection_id: str, data: Dict[str, Any]):
        """Handle service call from ROS"""
        service_name = data.get('service_name')
        service_type = data.get('service_type')
        request_data = data.get('request', {})
        
        # Process service call (this would integrate with cognitive processing)
        response_data = self._process_service_request(service_name, service_type, request_data)
        
        # Send response
        response_msg = ROSProtocol.pack_message(
            ROSProtocol.MSG_SERVICE_RESPONSE,
            {
                "service_name": service_name,
                "response": response_data,
                "timestamp": time.time()
            }
        )
        
        if connection_id in self.client_connections:
            try:
                self.client_connections[connection_id].send(response_msg)
            except Exception as e:
                logger.error(f"Service response error: {str(e)}")
    
    def _handle_action_goal(self, connection_id: str, data: Dict[str, Any]):
        """Handle action goal from ROS"""
        action_name = data.get('action_name')
        action_type = data.get('action_type')
        goal_data = data.get('goal', {})
        
        action = ROSAction(
            action_name=action_name,
            action_type=action_type,
            goal=goal_data,
            status="active"
        )
        
        self.active_actions[action.action_id] = action
        
        # Start action execution
        self.executor.submit(self._execute_ros_action, action, connection_id)
        
        logger.debug(f"Started action: {action_name}")
    
    def _handle_agent_state_update(self, connection_id: str, data: Dict[str, Any]):
        """Handle agent state update from ROS"""
        agent_id = data.get('agent_id')
        if not agent_id:
            return
        
        # Update or create agent
        if agent_id not in self.ros_agents:
            self.ros_agents[agent_id] = ROSCognitiveAgent(
                agent_id=agent_id,
                node_name=data.get('node_name', f"cognitive_agent_{agent_id}"),
                robot_type=data.get('robot_type', 'mobile_robot'),
                pose={},
                joint_states={},
                sensor_data={},
                actuator_states={},
                cognitive_state={},
                capabilities=data.get('capabilities', [])
            )
        
        agent = self.ros_agents[agent_id]
        
        # Update agent state
        if 'pose' in data:
            agent.pose.update(data['pose'])
        if 'joint_states' in data:
            agent.joint_states.update(data['joint_states'])
        if 'sensor_data' in data:
            agent.sensor_data.update(data['sensor_data'])
        if 'actuator_states' in data:
            agent.actuator_states.update(data['actuator_states'])
        if 'cognitive_state' in data:
            agent.cognitive_state.update(data['cognitive_state'])
        
        agent.last_update = time.time()
        
        logger.debug(f"Updated ROS agent: {agent_id}")
    
    def _handle_ros_heartbeat(self, connection_id: str, data: Dict[str, Any]):
        """Handle heartbeat from ROS"""
        # Update ROS system state if provided
        if 'system_state' in data:
            self.ros_system_state.update(data['system_state'])
        
        # Send heartbeat response
        response = ROSProtocol.pack_message(
            ROSProtocol.MSG_HEARTBEAT,
            {
                "status": "alive",
                "timestamp": time.time(),
                "active_agents": len(self.ros_agents),
                "active_topics": len(self.published_topics)
            }
        )
        
        if connection_id in self.client_connections:
            try:
                self.client_connections[connection_id].send(response)
            except Exception as e:
                logger.error(f"ROS heartbeat response error: {str(e)}")
    
    def _process_service_request(self, service_name: str, service_type: str, 
                                request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a ROS service request with cognitive integration"""
        # This would integrate with the cognitive processing system
        
        if service_name == "/cognitive/synthesize":
            # Neural-symbolic synthesis service
            symbolic_input = request_data.get('symbolic_input', {})
            neural_input = request_data.get('neural_input', [])
            
            # Simulate cognitive synthesis
            result = {
                "synthesis_result": [0.5] * 128,  # Placeholder
                "confidence": 0.85,
                "processing_time": 0.01
            }
            
            return {"success": True, "result": result}
        
        elif service_name == "/cognitive/attention":
            # Attention allocation service
            attention_focus = request_data.get('attention_focus', {})
            
            result = {
                "attention_weights": [0.8, 0.6, 0.4],  # Placeholder
                "focus_target": attention_focus.get('target', 'unknown')
            }
            
            return {"success": True, "result": result}
        
        else:
            # Generic service response
            return {"success": True, "message": f"Processed {service_name}"}
    
    def _execute_ros_action(self, action: ROSAction, connection_id: str):
        """Execute a ROS action"""
        try:
            # Simulate action execution with feedback
            for progress in range(0, 101, 10):
                if action.status != "active":
                    break
                
                # Send feedback
                feedback_msg = ROSProtocol.pack_message(
                    ROSProtocol.MSG_ACTION_FEEDBACK,
                    {
                        "action_id": action.action_id,
                        "feedback": {
                            "progress": progress,
                            "status": f"Processing... {progress}%"
                        },
                        "timestamp": time.time()
                    }
                )
                
                if connection_id in self.client_connections:
                    try:
                        self.client_connections[connection_id].send(feedback_msg)
                    except Exception as e:
                        logger.error(f"Action feedback error: {str(e)}")
                        break
                
                time.sleep(0.1)
            
            # Send result
            if action.status == "active":
                action.status = "succeeded"
                action.result = {
                    "success": True,
                    "final_state": action.goal,
                    "execution_time": time.time() - action.action_id.split('_')[-1]
                }
                
                result_msg = ROSProtocol.pack_message(
                    ROSProtocol.MSG_ACTION_RESULT,
                    {
                        "action_id": action.action_id,
                        "status": action.status,
                        "result": action.result,
                        "timestamp": time.time()
                    }
                )
                
                if connection_id in self.client_connections:
                    try:
                        self.client_connections[connection_id].send(result_msg)
                    except Exception as e:
                        logger.error(f"Action result error: {str(e)}")
        
        except Exception as e:
            action.status = "failed"
            action.result = {"error": str(e)}
            logger.error(f"Action execution error: {str(e)}")
    
    def _forward_message_to_connection(self, connection_id: str, message: ROSMessage):
        """Forward a ROS message to a specific connection"""
        msg = ROSProtocol.pack_message(
            ROSProtocol.MSG_PUBLISH,
            {
                "topic": message.topic,
                "message_type": message.message_type,
                "data": message.data,
                "frame_id": message.frame_id,
                "timestamp": message.timestamp
            }
        )
        
        if connection_id in self.client_connections:
            try:
                self.client_connections[connection_id].send(msg)
            except Exception as e:
                logger.error(f"Message forward error: {str(e)}")
    
    def _cleanup_ros_connection(self, connection_id: str):
        """Clean up a disconnected ROS connection"""
        if connection_id in self.client_connections:
            del self.client_connections[connection_id]
        
        if connection_id in self.connection_threads:
            del self.connection_threads[connection_id]
        
        logger.info(f"Cleaned up ROS connection: {connection_id}")
    
    def _monitor_ros_system(self):
        """Monitor ROS system state"""
        while self.running:
            try:
                # Simulate ROS system monitoring
                # In real implementation, this would use rospy or rclpy
                self.ros_system_state["active_nodes"] = list(self.client_connections.keys())
                self.ros_system_state["available_topics"] = list(self.published_topics.keys())
                self.ros_system_state["available_services"] = list(self.active_services.keys())
                
                time.sleep(5)  # Update every 5 seconds
                
            except Exception as e:
                logger.error(f"ROS system monitoring error: {str(e)}")
    
    def _process_messages(self):
        """Process outgoing messages to ROS"""
        while self.running:
            try:
                if self.outgoing_messages:
                    message = self.outgoing_messages.pop(0)
                    self._send_message_to_ros(message)
                
                time.sleep(0.01)
                
            except Exception as e:
                logger.error(f"ROS message processing error: {str(e)}")
    
    def _send_message_to_ros(self, message: Dict[str, Any]):
        """Send a message to ROS clients"""
        target_connection = message.get('target_connection')
        msg_type = message.get('msg_type')
        data = message.get('data', {})
        
        packed_message = ROSProtocol.pack_message(msg_type, data)
        
        if target_connection and target_connection in self.client_connections:
            try:
                self.client_connections[target_connection].send(packed_message)
            except Exception as e:
                logger.error(f"ROS send message error: {str(e)}")
        else:
            # Broadcast to all connections
            for conn_id, conn in self.client_connections.items():
                try:
                    conn.send(packed_message)
                except Exception as e:
                    logger.error(f"ROS broadcast error to {conn_id}: {str(e)}")
    
    def publish_topic(self, topic: str, message_type: str, data: Dict[str, Any], frame_id: str = ""):
        """Publish a message to a ROS topic"""
        message = {
            'msg_type': ROSProtocol.MSG_PUBLISH,
            'data': {
                'topic': topic,
                'message_type': message_type,
                'data': data,
                'frame_id': frame_id,
                'timestamp': time.time()
            }
        }
        self.outgoing_messages.append(message)
    
    def call_service(self, service_name: str, service_type: str, request: Dict[str, Any]):
        """Call a ROS service"""
        message = {
            'msg_type': ROSProtocol.MSG_SERVICE_CALL,
            'data': {
                'service_name': service_name,
                'service_type': service_type,
                'request': request,
                'timestamp': time.time()
            }
        }
        self.outgoing_messages.append(message)
    
    def send_cognitive_update(self, agent_id: str, cognitive_state: Dict[str, Any]):
        """Send cognitive state update to ROS agent"""
        message = {
            'msg_type': ROSProtocol.MSG_COGNITIVE_UPDATE,
            'data': {
                'agent_id': agent_id,
                'cognitive_state': cognitive_state,
                'timestamp': time.time()
            }
        }
        self.outgoing_messages.append(message)
    
    def get_agent_state(self, agent_id: str) -> Optional[ROSCognitiveAgent]:
        """Get the current state of a ROS agent"""
        return self.ros_agents.get(agent_id)
    
    def list_agents(self) -> List[ROSCognitiveAgent]:
        """List all ROS agents"""
        return list(self.ros_agents.values())
    
    def get_system_state(self) -> Dict[str, Any]:
        """Get current ROS system state"""
        return self.ros_system_state.copy()
    
    def get_status(self) -> Dict[str, Any]:
        """Get adapter status"""
        return {
            "running": self.running,
            "port": self.port,
            "ros_master_uri": self.ros_master_uri,
            "active_connections": len(self.client_connections),
            "ros_agents": len(self.ros_agents),
            "published_topics": len(self.published_topics),
            "active_actions": len(self.active_actions),
            "system_state": self.ros_system_state,
            "timestamp": time.time()
        }


def main():
    """Test ROS integration adapter"""
    import argparse
    
    parser = argparse.ArgumentParser(description="ROS Integration Adapter")
    parser.add_argument("--port", type=int, default=8888, help="Port to bind to")
    parser.add_argument("--ros-master-uri", default="http://localhost:11311", 
                       help="ROS Master URI")
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    adapter = ROSIntegrationAdapter(port=args.port, ros_master_uri=args.ros_master_uri)
    
    try:
        adapter.start_server()
        
        print(f"ROS Integration Adapter running on port {args.port}")
        print(f"ROS Master URI: {args.ros_master_uri}")
        print("Press Ctrl+C to stop...")
        
        while True:
            time.sleep(1)
            
            # Print status every 10 seconds
            if int(time.time()) % 10 == 0:
                status = adapter.get_status()
                print(f"Status: {status['active_connections']} connections, "
                      f"{status['ros_agents']} agents, "
                      f"{status['published_topics']} topics")
    
    except KeyboardInterrupt:
        print("\nShutting down...")
        adapter.stop_server()
    except Exception as e:
        print(f"Error: {str(e)}")
        adapter.stop_server()


if __name__ == "__main__":
    main()