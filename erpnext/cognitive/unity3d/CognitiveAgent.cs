using System;
using System.Collections;
using System.Collections.Generic;
using System.Net.Sockets;
using System.Text;
using UnityEngine;
using Newtonsoft.Json;

/// <summary>
/// Cognitive Agent SDK for Unity3D Integration
/// Provides C# interface for Unity3D cognitive agents to connect to the distributed cognitive mesh
/// </summary>
namespace CognitiveMesh
{
    [System.Serializable]
    public class CognitiveState
    {
        public string attention_focus;
        public float confidence;
        public Vector3 navigation_goal;
        public Dictionary<string, object> custom_properties = new Dictionary<string, object>();
    }

    [System.Serializable]
    public class TransformData
    {
        public float[] position = new float[3];
        public float[] rotation = new float[4];
        public float[] scale = new float[3];

        public static TransformData FromUnityTransform(Transform transform)
        {
            var data = new TransformData();
            data.position[0] = transform.position.x;
            data.position[1] = transform.position.y;
            data.position[2] = transform.position.z;
            
            data.rotation[0] = transform.rotation.x;
            data.rotation[1] = transform.rotation.y;
            data.rotation[2] = transform.rotation.z;
            data.rotation[3] = transform.rotation.w;
            
            data.scale[0] = transform.localScale.x;
            data.scale[1] = transform.localScale.y;
            data.scale[2] = transform.localScale.z;
            
            return data;
        }
    }

    [System.Serializable]
    public class CognitiveMessage
    {
        public int msg_type;
        public Dictionary<string, object> data = new Dictionary<string, object>();
    }

    public class CognitiveAgent : MonoBehaviour
    {
        [Header("Cognitive Mesh Configuration")]
        public string serverHost = "localhost";
        public int serverPort = 7777;
        public string agentId;
        public List<string> capabilities = new List<string> { "movement", "vision" };

        [Header("Agent State")]
        public CognitiveState cognitiveState = new CognitiveState();
        public bool isConnected = false;

        // Network components
        private TcpClient tcpClient;
        private NetworkStream stream;
        private byte[] receiveBuffer = new byte[4096];
        private Queue<CognitiveMessage> incomingMessages = new Queue<CognitiveMessage>();
        private Queue<CognitiveMessage> outgoingMessages = new Queue<CognitiveMessage>();

        // Protocol message types (match Unity3DProtocol in Python)
        private const int MSG_HANDSHAKE = 0x01;
        private const int MSG_AGENT_UPDATE = 0x02;
        private const int MSG_ACTION_REQUEST = 0x03;
        private const int MSG_ACTION_RESPONSE = 0x04;
        private const int MSG_SENSOR_DATA = 0x05;
        private const int MSG_COGNITIVE_STATE = 0x06;
        private const int MSG_HEARTBEAT = 0x07;

        // Update frequency control
        private float lastHeartbeat = 0f;
        private float heartbeatInterval = 5f; // seconds
        private float lastTransformUpdate = 0f;
        private float transformUpdateInterval = 0.1f; // 10 Hz
        private Vector3 lastPosition;
        private Quaternion lastRotation;

        void Start()
        {
            if (string.IsNullOrEmpty(agentId))
            {
                agentId = $"unity_agent_{gameObject.name}_{DateTime.Now.Ticks}";
            }

            StartCoroutine(ConnectToCognitiveMesh());
            
            // Initialize tracking variables
            lastPosition = transform.position;
            lastRotation = transform.rotation;
        }

        void Update()
        {
            if (isConnected)
            {
                ProcessIncomingMessages();
                ProcessOutgoingMessages();
                UpdateHeartbeat();
                UpdateTransformIfChanged();
            }
        }

        IEnumerator ConnectToCognitiveMesh()
        {
            Debug.Log($"[CognitiveAgent] Connecting to cognitive mesh at {serverHost}:{serverPort}");
            
            try
            {
                tcpClient = new TcpClient();
                yield return StartCoroutine(ConnectWithTimeout(tcpClient, serverHost, serverPort, 5.0f));
                
                stream = tcpClient.GetStream();
                isConnected = true;
                
                Debug.Log($"[CognitiveAgent] Connected to cognitive mesh. Agent ID: {agentId}");
                
                // Send initial agent registration
                SendAgentUpdate();
                
                // Start receiving data
                StartCoroutine(ReceiveData());
            }
            catch (Exception e)
            {
                Debug.LogError($"[CognitiveAgent] Connection failed: {e.Message}");
                isConnected = false;
            }
        }

        IEnumerator ConnectWithTimeout(TcpClient client, string host, int port, float timeout)
        {
            var connectTask = client.ConnectAsync(host, port);
            float elapsed = 0f;
            
            while (!connectTask.IsCompleted && elapsed < timeout)
            {
                elapsed += Time.deltaTime;
                yield return null;
            }
            
            if (!connectTask.IsCompleted)
            {
                throw new TimeoutException("Connection timeout");
            }
            
            if (connectTask.Exception != null)
            {
                throw connectTask.Exception;
            }
        }

        IEnumerator ReceiveData()
        {
            while (isConnected && tcpClient.Connected)
            {
                try
                {
                    if (stream.DataAvailable)
                    {
                        int bytesRead = stream.Read(receiveBuffer, 0, receiveBuffer.Length);
                        if (bytesRead > 0)
                        {
                            ProcessReceivedData(receiveBuffer, bytesRead);
                        }
                    }
                }
                catch (Exception e)
                {
                    Debug.LogError($"[CognitiveAgent] Receive error: {e.Message}");
                    Disconnect();
                    break;
                }
                
                yield return new WaitForSeconds(0.01f); // 100 Hz polling
            }
        }

        void ProcessReceivedData(byte[] data, int length)
        {
            // Parse the received data according to Unity3D protocol
            // This is a simplified implementation - real version would handle partial messages
            if (length >= 5) // Minimum header size
            {
                try
                {
                    int msgType = data[0];
                    int dataLength = BitConverter.ToInt32(data, 1);
                    
                    if (length >= 5 + dataLength)
                    {
                        string jsonData = Encoding.UTF8.GetString(data, 5, dataLength);
                        var messageData = JsonConvert.DeserializeObject<Dictionary<string, object>>(jsonData);
                        
                        var message = new CognitiveMessage
                        {
                            msg_type = msgType,
                            data = messageData
                        };
                        
                        incomingMessages.Enqueue(message);
                    }
                }
                catch (Exception e)
                {
                    Debug.LogError($"[CognitiveAgent] Message parsing error: {e.Message}");
                }
            }
        }

        void ProcessIncomingMessages()
        {
            while (incomingMessages.Count > 0)
            {
                var message = incomingMessages.Dequeue();
                HandleCognitiveMessage(message);
            }
        }

        void HandleCognitiveMessage(CognitiveMessage message)
        {
            switch (message.msg_type)
            {
                case MSG_HANDSHAKE:
                    HandleHandshake(message.data);
                    break;
                case MSG_ACTION_REQUEST:
                    HandleActionRequest(message.data);
                    break;
                case MSG_COGNITIVE_STATE:
                    HandleCognitiveStateUpdate(message.data);
                    break;
                case MSG_HEARTBEAT:
                    HandleHeartbeat(message.data);
                    break;
                default:
                    Debug.LogWarning($"[CognitiveAgent] Unknown message type: {message.msg_type}");
                    break;
            }
        }

        void HandleHandshake(Dictionary<string, object> data)
        {
            Debug.Log($"[CognitiveAgent] Handshake received from server");
            if (data.ContainsKey("server_version"))
            {
                Debug.Log($"[CognitiveAgent] Server version: {data["server_version"]}");
            }
        }

        void HandleActionRequest(Dictionary<string, object> data)
        {
            string actionId = data.ContainsKey("action_id") ? data["action_id"].ToString() : "";
            string actionType = data.ContainsKey("action_type") ? data["action_type"].ToString() : "";
            
            Debug.Log($"[CognitiveAgent] Action request: {actionType} (ID: {actionId})");
            
            // Execute the action based on type
            bool success = ExecuteAction(actionType, data);
            
            // Send action response
            SendActionResponse(actionId, success ? "completed" : "failed");
        }

        void HandleCognitiveStateUpdate(Dictionary<string, object> data)
        {
            Debug.Log($"[CognitiveAgent] Cognitive state update received");
            // Update local cognitive state based on distributed mesh state
            // This would typically update AI behavior, attention, goals, etc.
        }

        void HandleHeartbeat(Dictionary<string, object> data)
        {
            // Server heartbeat - connection is alive
        }

        bool ExecuteAction(string actionType, Dictionary<string, object> parameters)
        {
            switch (actionType)
            {
                case "move":
                    return ExecuteMovement(parameters);
                case "rotate":
                    return ExecuteRotation(parameters);
                case "interact":
                    return ExecuteInteraction(parameters);
                default:
                    Debug.LogWarning($"[CognitiveAgent] Unknown action type: {actionType}");
                    return false;
            }
        }

        bool ExecuteMovement(Dictionary<string, object> parameters)
        {
            if (parameters.ContainsKey("target_position"))
            {
                var targetPos = parameters["target_position"] as float[];
                if (targetPos != null && targetPos.Length >= 3)
                {
                    Vector3 target = new Vector3(targetPos[0], targetPos[1], targetPos[2]);
                    
                    // Simple movement - in practice you'd use proper pathfinding/movement system
                    StartCoroutine(MoveToPosition(target));
                    return true;
                }
            }
            return false;
        }

        bool ExecuteRotation(Dictionary<string, object> parameters)
        {
            if (parameters.ContainsKey("target_rotation"))
            {
                var targetRot = parameters["target_rotation"] as float[];
                if (targetRot != null && targetRot.Length >= 4)
                {
                    Quaternion target = new Quaternion(targetRot[0], targetRot[1], targetRot[2], targetRot[3]);
                    StartCoroutine(RotateToRotation(target));
                    return true;
                }
            }
            return false;
        }

        bool ExecuteInteraction(Dictionary<string, object> parameters)
        {
            // Implement object interaction logic
            Debug.Log($"[CognitiveAgent] Executing interaction");
            return true;
        }

        IEnumerator MoveToPosition(Vector3 target)
        {
            float duration = 2.0f;
            Vector3 startPos = transform.position;
            float elapsed = 0f;
            
            while (elapsed < duration)
            {
                elapsed += Time.deltaTime;
                float t = elapsed / duration;
                transform.position = Vector3.Lerp(startPos, target, t);
                yield return null;
            }
            
            transform.position = target;
        }

        IEnumerator RotateToRotation(Quaternion target)
        {
            float duration = 1.0f;
            Quaternion startRot = transform.rotation;
            float elapsed = 0f;
            
            while (elapsed < duration)
            {
                elapsed += Time.deltaTime;
                float t = elapsed / duration;
                transform.rotation = Quaternion.Lerp(startRot, target, t);
                yield return null;
            }
            
            transform.rotation = target;
        }

        void ProcessOutgoingMessages()
        {
            while (outgoingMessages.Count > 0)
            {
                var message = outgoingMessages.Dequeue();
                SendMessage(message);
            }
        }

        void SendMessage(CognitiveMessage message)
        {
            if (!isConnected || stream == null) return;
            
            try
            {
                string jsonData = JsonConvert.SerializeObject(message.data);
                byte[] jsonBytes = Encoding.UTF8.GetBytes(jsonData);
                
                // Create message with header: [msg_type:1][length:4][data:n]
                byte[] messageBytes = new byte[5 + jsonBytes.Length];
                messageBytes[0] = (byte)message.msg_type;
                BitConverter.GetBytes(jsonBytes.Length).CopyTo(messageBytes, 1);
                jsonBytes.CopyTo(messageBytes, 5);
                
                stream.Write(messageBytes, 0, messageBytes.Length);
            }
            catch (Exception e)
            {
                Debug.LogError($"[CognitiveAgent] Send error: {e.Message}");
            }
        }

        void UpdateHeartbeat()
        {
            if (Time.time - lastHeartbeat >= heartbeatInterval)
            {
                SendHeartbeat();
                lastHeartbeat = Time.time;
            }
        }

        void UpdateTransformIfChanged()
        {
            if (Time.time - lastTransformUpdate >= transformUpdateInterval)
            {
                bool positionChanged = Vector3.Distance(transform.position, lastPosition) > 0.01f;
                bool rotationChanged = Quaternion.Angle(transform.rotation, lastRotation) > 1f;
                
                if (positionChanged || rotationChanged)
                {
                    SendAgentUpdate();
                    lastPosition = transform.position;
                    lastRotation = transform.rotation;
                }
                
                lastTransformUpdate = Time.time;
            }
        }

        public void SendAgentUpdate()
        {
            var message = new CognitiveMessage
            {
                msg_type = MSG_AGENT_UPDATE,
                data = new Dictionary<string, object>
                {
                    ["agent_id"] = agentId,
                    ["game_object_name"] = gameObject.name,
                    ["transform"] = TransformData.FromUnityTransform(transform),
                    ["cognitive_state"] = cognitiveState,
                    ["capabilities"] = capabilities,
                    ["timestamp"] = DateTimeOffset.Now.ToUnixTimeSeconds()
                }
            };
            
            outgoingMessages.Enqueue(message);
        }

        public void SendSensorData(string sensorType, Dictionary<string, object> sensorData)
        {
            var message = new CognitiveMessage
            {
                msg_type = MSG_SENSOR_DATA,
                data = new Dictionary<string, object>
                {
                    ["agent_id"] = agentId,
                    ["sensor_type"] = sensorType,
                    ["data"] = sensorData,
                    ["timestamp"] = DateTimeOffset.Now.ToUnixTimeSeconds()
                }
            };
            
            outgoingMessages.Enqueue(message);
        }

        public void SendActionResponse(string actionId, string status)
        {
            var message = new CognitiveMessage
            {
                msg_type = MSG_ACTION_RESPONSE,
                data = new Dictionary<string, object>
                {
                    ["action_id"] = actionId,
                    ["agent_id"] = agentId,
                    ["status"] = status,
                    ["timestamp"] = DateTimeOffset.Now.ToUnixTimeSeconds()
                }
            };
            
            outgoingMessages.Enqueue(message);
        }

        void SendHeartbeat()
        {
            var message = new CognitiveMessage
            {
                msg_type = MSG_HEARTBEAT,
                data = new Dictionary<string, object>
                {
                    ["agent_id"] = agentId,
                    ["status"] = "alive",
                    ["timestamp"] = DateTimeOffset.Now.ToUnixTimeSeconds()
                }
            };
            
            outgoingMessages.Enqueue(message);
        }

        public void UpdateCognitiveState(string attentionFocus, float confidence, Vector3 navigationGoal)
        {
            cognitiveState.attention_focus = attentionFocus;
            cognitiveState.confidence = confidence;
            cognitiveState.navigation_goal = navigationGoal;
            
            var message = new CognitiveMessage
            {
                msg_type = MSG_COGNITIVE_STATE,
                data = new Dictionary<string, object>
                {
                    ["agent_id"] = agentId,
                    ["cognitive_state"] = cognitiveState,
                    ["timestamp"] = DateTimeOffset.Now.ToUnixTimeSeconds()
                }
            };
            
            outgoingMessages.Enqueue(message);
        }

        public void Disconnect()
        {
            if (isConnected)
            {
                isConnected = false;
                
                try
                {
                    stream?.Close();
                    tcpClient?.Close();
                }
                catch (Exception e)
                {
                    Debug.LogError($"[CognitiveAgent] Disconnect error: {e.Message}");
                }
                
                Debug.Log($"[CognitiveAgent] Disconnected from cognitive mesh");
            }
        }

        void OnDestroy()
        {
            Disconnect();
        }

        void OnApplicationQuit()
        {
            Disconnect();
        }
    }
}