#!/usr/bin/env python3
"""
Cognitive ROS Client Package

Provides ROS integration for the distributed cognitive mesh.
This package allows ROS nodes to connect to and interact with
the cognitive API server for embodied cognition.
"""

import rospy
import json
import time
import socket
import struct
import threading
import numpy as np
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
import queue

# ROS imports
try:
    import rospy
    from std_msgs.msg import String, Float32, Bool
    from geometry_msgs.msg import Pose, PoseStamped, Twist, Transform
    from sensor_msgs.msg import LaserScan, Image, PointCloud2, Imu, JointState
    from nav_msgs.msg import Odometry, OccupancyGrid
    ROS_AVAILABLE = True
except ImportError:
    print("ROS not available - using stubs")
    ROS_AVAILABLE = False


@dataclass
class CognitiveRosMessage:
    """Represents a message in the cognitive ROS protocol"""
    topic: str
    message_type: str
    data: Dict[str, Any]
    timestamp: float = 0.0
    frame_id: str = ""

    def __post_init__(self):
        if self.timestamp == 0.0:
            self.timestamp = time.time()


class CognitiveRosClient:
    """
    ROS client for connecting to the distributed cognitive mesh
    
    This class provides a bridge between ROS and the cognitive API server,
    allowing ROS nodes to participate in distributed cognitive processing.
    """

    def __init__(self, 
                 server_host: str = "localhost", 
                 server_port: int = 8888,
                 node_name: str = "cognitive_ros_client",
                 robot_type: str = "mobile_robot"):
        
        self.server_host = server_host
        self.server_port = server_port
        self.node_name = node_name
        self.robot_type = robot_type
        self.agent_id = f"ros_{robot_type}_{int(time.time())}"
        
        # Connection management
        self.socket = None
        self.connected = False
        self.running = False
        
        # Message queues
        self.outgoing_messages = queue.Queue()
        self.incoming_messages = queue.Queue()
        
        # ROS state
        self.pose = {"x": 0.0, "y": 0.0, "z": 0.0, "theta": 0.0}
        self.joint_states = {}
        self.sensor_data = {}
        self.actuator_states = {}
        self.cognitive_state = {}
        self.capabilities = ["navigation", "perception", "manipulation"]
        
        # ROS publishers and subscribers
        self.publishers = {}
        self.subscribers = {}
        self.services = {}
        
        # Protocol constants
        self.MSG_PUBLISH = 0x10
        self.MSG_SUBSCRIBE = 0x11
        self.MSG_SERVICE_CALL = 0x12
        self.MSG_SERVICE_RESPONSE = 0x13
        self.MSG_ACTION_GOAL = 0x14
        self.MSG_ACTION_FEEDBACK = 0x15
        self.MSG_ACTION_RESULT = 0x16
        self.MSG_AGENT_STATE = 0x17
        self.MSG_COGNITIVE_UPDATE = 0x18
        self.MSG_HEARTBEAT = 0x19

        # Initialize ROS node if available
        if ROS_AVAILABLE:
            try:
                rospy.init_node(node_name, anonymous=True)
                self.setup_ros_publishers_and_subscribers()
                rospy.loginfo(f"[CognitiveRosClient] ROS node '{node_name}' initialized")
            except Exception as e:
                rospy.logerr(f"[CognitiveRosClient] ROS initialization failed: {e}")
                ROS_AVAILABLE = False

    def setup_ros_publishers_and_subscribers(self):
        """Setup ROS publishers and subscribers"""
        if not ROS_AVAILABLE:
            return

        # Publishers for cognitive outputs
        self.publishers['cognitive_state'] = rospy.Publisher(
            '/cognitive/state', String, queue_size=10
        )
        self.publishers['attention_focus'] = rospy.Publisher(
            '/cognitive/attention', String, queue_size=10
        )
        self.publishers['synthesis_result'] = rospy.Publisher(
            '/cognitive/synthesis', String, queue_size=10
        )

        # Subscribers for robot state
        self.subscribers['odom'] = rospy.Subscriber(
            '/odom', Odometry, self.odometry_callback
        )
        self.subscribers['laser'] = rospy.Subscriber(
            '/scan', LaserScan, self.laser_callback
        )
        self.subscribers['joint_states'] = rospy.Subscriber(
            '/joint_states', JointState, self.joint_states_callback
        )
        self.subscribers['cmd_vel'] = rospy.Subscriber(
            '/cmd_vel', Twist, self.cmd_vel_callback
        )

        rospy.loginfo("[CognitiveRosClient] ROS publishers and subscribers setup complete")

    def connect_to_cognitive_mesh(self):
        """Connect to the cognitive API server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.server_host, self.server_port))
            self.connected = True
            self.running = True
            
            print(f"[CognitiveRosClient] Connected to cognitive mesh at {self.server_host}:{self.server_port}")
            
            # Start communication threads
            threading.Thread(target=self._receive_messages, daemon=True).start()
            threading.Thread(target=self._send_messages, daemon=True).start()
            threading.Thread(target=self._heartbeat_loop, daemon=True).start()
            
            # Send initial agent registration
            self.send_agent_state_update()
            
            return True
            
        except Exception as e:
            print(f"[CognitiveRosClient] Connection failed: {e}")
            self.connected = False
            return False

    def disconnect(self):
        """Disconnect from the cognitive mesh"""
        self.running = False
        self.connected = False
        
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        
        print("[CognitiveRosClient] Disconnected from cognitive mesh")

    def _pack_message(self, msg_type: int, data: Dict[str, Any]) -> bytes:
        """Pack a message for transmission"""
        json_data = json.dumps(data, default=str).encode('utf-8')
        header = struct.pack('!BI', msg_type, len(json_data))
        return header + json_data

    def _unpack_message(self, data: bytes) -> tuple:
        """Unpack a received message"""
        if len(data) < 5:
            raise ValueError("Message too short")
        
        msg_type, data_length = struct.unpack('!BI', data[:5])
        json_data = data[5:5+data_length].decode('utf-8')
        
        return msg_type, json.loads(json_data)

    def _receive_messages(self):
        """Receive messages from the cognitive mesh"""
        buffer = b""
        
        while self.running and self.connected:
            try:
                data = self.socket.recv(4096)
                if not data:
                    break
                
                buffer += data
                
                # Process complete messages
                while len(buffer) >= 5:
                    msg_type, data_length = struct.unpack('!BI', buffer[:5])
                    total_length = 5 + data_length
                    
                    if len(buffer) < total_length:
                        break
                    
                    message_data = buffer[:total_length]
                    buffer = buffer[total_length:]
                    
                    # Process the message
                    self._process_cognitive_message(message_data)
                    
            except Exception as e:
                if self.running:
                    print(f"[CognitiveRosClient] Receive error: {e}")
                break

    def _send_messages(self):
        """Send queued messages to the cognitive mesh"""
        while self.running and self.connected:
            try:
                if not self.outgoing_messages.empty():
                    message = self.outgoing_messages.get(timeout=1.0)
                    self.socket.send(message)
            except queue.Empty:
                continue
            except Exception as e:
                if self.running:
                    print(f"[CognitiveRosClient] Send error: {e}")
                break

    def _heartbeat_loop(self):
        """Send periodic heartbeat messages"""
        while self.running and self.connected:
            try:
                self.send_heartbeat()
                time.sleep(5.0)  # 5 second heartbeat
            except Exception as e:
                print(f"[CognitiveRosClient] Heartbeat error: {e}")
                break

    def _process_cognitive_message(self, message_data: bytes):
        """Process a message received from the cognitive mesh"""
        try:
            msg_type, data = self._unpack_message(message_data)
            
            if msg_type == self.MSG_COGNITIVE_UPDATE:
                self._handle_cognitive_update(data)
            elif msg_type == self.MSG_ACTION_GOAL:
                self._handle_action_goal(data)
            elif msg_type == self.MSG_SERVICE_CALL:
                self._handle_service_call(data)
            elif msg_type == self.MSG_HEARTBEAT:
                self._handle_heartbeat(data)
            else:
                print(f"[CognitiveRosClient] Unknown message type: {msg_type}")
                
        except Exception as e:
            print(f"[CognitiveRosClient] Message processing error: {e}")

    def _handle_cognitive_update(self, data: Dict[str, Any]):
        """Handle cognitive state update from the mesh"""
        print(f"[CognitiveRosClient] Cognitive update received")
        
        # Update local cognitive state
        if 'cognitive_state' in data:
            self.cognitive_state.update(data['cognitive_state'])
        
        # Publish to ROS if available
        if ROS_AVAILABLE and 'cognitive_state' in self.publishers:
            cognitive_msg = String()
            cognitive_msg.data = json.dumps(self.cognitive_state)
            self.publishers['cognitive_state'].publish(cognitive_msg)

    def _handle_action_goal(self, data: Dict[str, Any]):
        """Handle action goal from the cognitive mesh"""
        action_name = data.get('action_name', '')
        action_type = data.get('action_type', '')
        goal_data = data.get('goal', {})
        
        print(f"[CognitiveRosClient] Action goal: {action_name} ({action_type})")
        
        # Execute the action based on type
        success = self._execute_action(action_type, goal_data)
        
        # Send result back
        self.send_action_result(data.get('action_id', ''), success)

    def _handle_service_call(self, data: Dict[str, Any]):
        """Handle service call from the cognitive mesh"""
        service_name = data.get('service_name', '')
        request_data = data.get('request', {})
        
        print(f"[CognitiveRosClient] Service call: {service_name}")
        
        # Process the service request
        response = self._process_service_request(service_name, request_data)
        
        # Send response back
        self.send_service_response(service_name, response)

    def _handle_heartbeat(self, data: Dict[str, Any]):
        """Handle heartbeat from the cognitive mesh"""
        # Connection is alive - no action needed
        pass

    def _execute_action(self, action_type: str, goal_data: Dict[str, Any]) -> bool:
        """Execute an action requested by the cognitive mesh"""
        try:
            if action_type == "navigate_to_goal":
                return self._execute_navigation(goal_data)
            elif action_type == "manipulate_object":
                return self._execute_manipulation(goal_data)
            elif action_type == "observe_environment":
                return self._execute_observation(goal_data)
            else:
                print(f"[CognitiveRosClient] Unknown action type: {action_type}")
                return False
        except Exception as e:
            print(f"[CognitiveRosClient] Action execution error: {e}")
            return False

    def _execute_navigation(self, goal_data: Dict[str, Any]) -> bool:
        """Execute navigation action"""
        target_pose = goal_data.get('target_pose', {})
        
        if ROS_AVAILABLE and 'cmd_vel' in self.publishers:
            # Simple navigation - move towards target
            # In practice, you'd use proper navigation stack
            twist = Twist()
            twist.linear.x = 0.5  # Forward velocity
            twist.angular.z = 0.0  # No rotation for simplicity
            
            # This would be replaced with proper navigation logic
            print(f"[CognitiveRosClient] Navigating to: {target_pose}")
            
            return True
        
        return False

    def _execute_manipulation(self, goal_data: Dict[str, Any]) -> bool:
        """Execute manipulation action"""
        target_object = goal_data.get('target_object', '')
        action = goal_data.get('action', 'grasp')
        
        print(f"[CognitiveRosClient] Manipulating {target_object}: {action}")
        
        # This would interface with manipulation controllers
        return True

    def _execute_observation(self, goal_data: Dict[str, Any]) -> bool:
        """Execute observation action"""
        observation_type = goal_data.get('observation_type', 'general')
        
        print(f"[CognitiveRosClient] Observing environment: {observation_type}")
        
        # Process sensor data and send to cognitive mesh
        observation_data = {
            'laser_data': list(self.sensor_data.get('laser_ranges', [])),
            'pose': self.pose,
            'timestamp': time.time()
        }
        
        self.send_sensor_data('environment_observation', observation_data)
        return True

    def _process_service_request(self, service_name: str, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a service request from the cognitive mesh"""
        if service_name == "/cognitive/get_pose":
            return {"pose": self.pose, "success": True}
        elif service_name == "/cognitive/get_sensor_data":
            return {"sensor_data": self.sensor_data, "success": True}
        elif service_name == "/cognitive/synthesize":
            # Perform cognitive synthesis
            symbolic_input = request_data.get('symbolic_input', {})
            neural_input = request_data.get('neural_input', [])
            
            # This would interface with the neural-symbolic synthesizer
            result = {"synthesis_result": [0.5] * 128, "confidence": 0.85}
            return {"result": result, "success": True}
        else:
            return {"error": f"Unknown service: {service_name}", "success": False}

    # ROS Callback functions
    def odometry_callback(self, msg):
        """Handle odometry messages from ROS"""
        if not ROS_AVAILABLE:
            return
            
        self.pose = {
            "x": msg.pose.pose.position.x,
            "y": msg.pose.pose.position.y,
            "z": msg.pose.pose.position.z,
            "theta": 2 * np.arctan2(msg.pose.pose.orientation.z, msg.pose.pose.orientation.w)
        }
        
        # Send updated pose to cognitive mesh
        if self.connected:
            self.send_agent_state_update()

    def laser_callback(self, msg):
        """Handle laser scan messages from ROS"""
        if not ROS_AVAILABLE:
            return
            
        self.sensor_data['laser_ranges'] = list(msg.ranges)
        self.sensor_data['laser_angle_min'] = msg.angle_min
        self.sensor_data['laser_angle_max'] = msg.angle_max
        self.sensor_data['laser_timestamp'] = msg.header.stamp.to_sec()
        
        # Send sensor data to cognitive mesh
        if self.connected:
            self.send_sensor_data('laser_scan', {
                'ranges': list(msg.ranges),
                'angle_min': msg.angle_min,
                'angle_max': msg.angle_max,
                'range_min': msg.range_min,
                'range_max': msg.range_max
            })

    def joint_states_callback(self, msg):
        """Handle joint state messages from ROS"""
        if not ROS_AVAILABLE:
            return
            
        for i, name in enumerate(msg.name):
            if i < len(msg.position):
                self.joint_states[name] = msg.position[i]

    def cmd_vel_callback(self, msg):
        """Handle velocity command messages from ROS"""
        if not ROS_AVAILABLE:
            return
            
        self.actuator_states['linear_velocity'] = msg.linear.x
        self.actuator_states['angular_velocity'] = msg.angular.z

    # Message sending functions
    def send_agent_state_update(self):
        """Send agent state update to cognitive mesh"""
        message_data = {
            'agent_id': self.agent_id,
            'node_name': self.node_name,
            'robot_type': self.robot_type,
            'pose': self.pose,
            'joint_states': self.joint_states,
            'sensor_data': self.sensor_data,
            'actuator_states': self.actuator_states,
            'cognitive_state': self.cognitive_state,
            'capabilities': self.capabilities,
            'timestamp': time.time()
        }
        
        message = self._pack_message(self.MSG_AGENT_STATE, message_data)
        self.outgoing_messages.put(message)

    def send_sensor_data(self, sensor_type: str, data: Dict[str, Any]):
        """Send sensor data to cognitive mesh"""
        message_data = {
            'agent_id': self.agent_id,
            'sensor_type': sensor_type,
            'data': data,
            'timestamp': time.time()
        }
        
        message = self._pack_message(self.MSG_PUBLISH, message_data)
        self.outgoing_messages.put(message)

    def send_action_result(self, action_id: str, success: bool):
        """Send action result to cognitive mesh"""
        message_data = {
            'action_id': action_id,
            'agent_id': self.agent_id,
            'status': 'succeeded' if success else 'failed',
            'result': {'success': success},
            'timestamp': time.time()
        }
        
        message = self._pack_message(self.MSG_ACTION_RESULT, message_data)
        self.outgoing_messages.put(message)

    def send_service_response(self, service_name: str, response: Dict[str, Any]):
        """Send service response to cognitive mesh"""
        message_data = {
            'service_name': service_name,
            'response': response,
            'timestamp': time.time()
        }
        
        message = self._pack_message(self.MSG_SERVICE_RESPONSE, message_data)
        self.outgoing_messages.put(message)

    def send_heartbeat(self):
        """Send heartbeat to cognitive mesh"""
        message_data = {
            'agent_id': self.agent_id,
            'status': 'alive',
            'timestamp': time.time()
        }
        
        message = self._pack_message(self.MSG_HEARTBEAT, message_data)
        self.outgoing_messages.put(message)

    def update_cognitive_state(self, new_state: Dict[str, Any]):
        """Update the agent's cognitive state"""
        self.cognitive_state.update(new_state)
        
        if self.connected:
            message_data = {
                'agent_id': self.agent_id,
                'cognitive_state': self.cognitive_state,
                'timestamp': time.time()
            }
            
            message = self._pack_message(self.MSG_COGNITIVE_UPDATE, message_data)
            self.outgoing_messages.put(message)

    def run(self):
        """Main run loop for the cognitive ROS client"""
        print(f"[CognitiveRosClient] Starting cognitive ROS client for agent: {self.agent_id}")
        
        # Connect to cognitive mesh
        if not self.connect_to_cognitive_mesh():
            print("[CognitiveRosClient] Failed to connect to cognitive mesh")
            return False
        
        try:
            if ROS_AVAILABLE:
                # Use ROS spin
                rospy.spin()
            else:
                # Simple loop for non-ROS environments
                while self.running:
                    time.sleep(1.0)
                    
        except KeyboardInterrupt:
            print("[CognitiveRosClient] Interrupted by user")
        except Exception as e:
            print(f"[CognitiveRosClient] Error in run loop: {e}")
        finally:
            self.disconnect()
        
        return True


def main():
    """Main entry point for the cognitive ROS client"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Cognitive ROS Client")
    parser.add_argument("--server-host", default="localhost", help="Cognitive mesh server host")
    parser.add_argument("--server-port", type=int, default=8888, help="Cognitive mesh server port")
    parser.add_argument("--node-name", default="cognitive_ros_client", help="ROS node name")
    parser.add_argument("--robot-type", default="mobile_robot", help="Robot type")
    
    args = parser.parse_args()
    
    # Create and run the client
    client = CognitiveRosClient(
        server_host=args.server_host,
        server_port=args.server_port,
        node_name=args.node_name,
        robot_type=args.robot_type
    )
    
    success = client.run()
    exit(0 if success else 1)


if __name__ == "__main__":
    main()