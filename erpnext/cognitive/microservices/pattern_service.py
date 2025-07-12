"""
Pattern Matching Microservice

Provides REST API endpoints for template-based pattern recognition.
Implements modular pattern matching for cognitive grammar operations.
"""

import json
from typing import Dict, List, Any, Optional
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cognitive_grammar import PatternMatcher, AtomSpace


class PatternHTTPHandler(BaseHTTPRequestHandler):
    """HTTP request handler for pattern matching operations"""
    
    def do_POST(self):
        """Handle POST requests for pattern operations"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data.decode('utf-8'))
            
            if path == '/patterns':
                self._handle_define_pattern(data)
            elif path == '/match':
                self._handle_match_pattern(data)
            elif path == '/multi_match':
                self._handle_multi_pattern_match(data)
            elif path == '/scheme_pattern':
                self._handle_generate_scheme_pattern(data)
            else:
                self._send_error(404, "Endpoint not found")
        except json.JSONDecodeError:
            self._send_error(400, "Invalid JSON")
        except Exception as e:
            self._send_error(500, f"Internal server error: {str(e)}")
    
    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        query_params = parse_qs(parsed_path.query)
        
        try:
            if path == '/patterns':
                self._handle_list_patterns()
            elif path.startswith('/patterns/'):
                pattern_name = path.split('/')[-1]
                self._handle_get_pattern(pattern_name)
            elif path == '/health':
                self._handle_health_check()
            elif path == '/stats':
                self._handle_get_stats()
            else:
                self._send_error(404, "Endpoint not found")
        except Exception as e:
            self._send_error(500, f"Internal server error: {str(e)}")
    
    def do_DELETE(self):
        """Handle DELETE requests"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        try:
            if path.startswith('/patterns/'):
                pattern_name = path.split('/')[-1]
                self._handle_delete_pattern(pattern_name)
            else:
                self._send_error(404, "Endpoint not found")
        except Exception as e:
            self._send_error(500, f"Internal server error: {str(e)}")
    
    def _handle_define_pattern(self, data):
        """Handle pattern definition request"""
        try:
            pattern_name = data['pattern_name']
            template = data['template']
            
            pattern_matcher = self.server.pattern_matcher
            pattern_matcher.define_pattern(pattern_name, template)
            
            response = {
                "message": f"Pattern '{pattern_name}' defined successfully",
                "pattern_name": pattern_name,
                "template": template
            }
            
            self._send_json_response(response, status=201)
        except KeyError as e:
            self._send_error(400, f"Missing required field: {str(e)}")
        except Exception as e:
            self._send_error(500, f"Pattern definition error: {str(e)}")
    
    def _handle_match_pattern(self, data):
        """Handle pattern matching request"""
        try:
            pattern_name = data['pattern_name']
            target_atoms = data['target_atoms']
            
            pattern_matcher = self.server.pattern_matcher
            matches = pattern_matcher.match_pattern(pattern_name, target_atoms)
            
            response = {
                "pattern_name": pattern_name,
                "target_atoms": target_atoms,
                "matches": matches,
                "match_count": len(matches)
            }
            
            self._send_json_response(response)
        except KeyError as e:
            self._send_error(400, f"Missing required field: {str(e)}")
        except Exception as e:
            self._send_error(500, f"Pattern matching error: {str(e)}")
    
    def _handle_multi_pattern_match(self, data):
        """Handle multiple pattern matching request"""
        try:
            patterns = data['patterns']  # List of pattern names
            target_atoms = data['target_atoms']
            
            pattern_matcher = self.server.pattern_matcher
            all_matches = {}
            
            for pattern_name in patterns:
                matches = pattern_matcher.match_pattern(pattern_name, target_atoms)
                all_matches[pattern_name] = {
                    "matches": matches,
                    "match_count": len(matches)
                }
            
            response = {
                "patterns": patterns,
                "target_atoms": target_atoms,
                "results": all_matches,
                "total_patterns": len(patterns)
            }
            
            self._send_json_response(response)
        except KeyError as e:
            self._send_error(400, f"Missing required field: {str(e)}")
        except Exception as e:
            self._send_error(500, f"Multi-pattern matching error: {str(e)}")
    
    def _handle_generate_scheme_pattern(self, data):
        """Handle Scheme pattern generation request"""
        try:
            pattern_name = data['pattern_name']
            
            pattern_matcher = self.server.pattern_matcher
            scheme_spec = pattern_matcher.scheme_pattern_match(pattern_name)
            
            response = {
                "pattern_name": pattern_name,
                "scheme_specification": scheme_spec
            }
            
            self._send_json_response(response)
        except KeyError as e:
            self._send_error(400, f"Missing required field: {str(e)}")
        except Exception as e:
            self._send_error(500, f"Scheme generation error: {str(e)}")
    
    def _handle_list_patterns(self):
        """List all defined patterns"""
        pattern_matcher = self.server.pattern_matcher
        patterns = list(pattern_matcher.patterns.keys())
        
        response = {
            "patterns": patterns,
            "pattern_count": len(patterns)
        }
        
        self._send_json_response(response)
    
    def _handle_get_pattern(self, pattern_name):
        """Get specific pattern definition"""
        pattern_matcher = self.server.pattern_matcher
        
        if pattern_name in pattern_matcher.patterns:
            template = pattern_matcher.patterns[pattern_name]
            response = {
                "pattern_name": pattern_name,
                "template": template
            }
            self._send_json_response(response)
        else:
            self._send_error(404, f"Pattern not found: {pattern_name}")
    
    def _handle_delete_pattern(self, pattern_name):
        """Delete pattern definition"""
        pattern_matcher = self.server.pattern_matcher
        
        if pattern_name in pattern_matcher.patterns:
            del pattern_matcher.patterns[pattern_name]
            response = {
                "message": f"Pattern '{pattern_name}' deleted successfully"
            }
            self._send_json_response(response)
        else:
            self._send_error(404, f"Pattern not found: {pattern_name}")
    
    def _handle_health_check(self):
        """Health check endpoint"""
        self._send_json_response({
            "status": "healthy",
            "service": "pattern_matching",
            "version": "1.0.0"
        })
    
    def _handle_get_stats(self):
        """Get pattern matching service statistics"""
        pattern_matcher = self.server.pattern_matcher
        stats = {
            "total_patterns": len(pattern_matcher.patterns),
            "pattern_names": list(pattern_matcher.patterns.keys()),
            "atomspace_size": len(pattern_matcher.atomspace.atoms)
        }
        self._send_json_response(stats)
    
    def _send_json_response(self, data, status=200):
        """Send JSON response"""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response_json = json.dumps(data, indent=2)
        self.wfile.write(response_json.encode('utf-8'))
    
    def _send_error(self, status, message):
        """Send error response"""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        error_data = {"error": message, "status": status}
        response_json = json.dumps(error_data)
        self.wfile.write(response_json.encode('utf-8'))


class PatternService:
    """
    Pattern Matching Microservice
    
    Provides REST API for template-based pattern recognition.
    Implements modular pattern matching architecture.
    """
    
    def __init__(self, atomspace: AtomSpace = None, host='localhost', port=8003):
        self.host = host
        self.port = port
        self.atomspace = atomspace or AtomSpace()
        self.pattern_matcher = PatternMatcher(self.atomspace)
        self.server = None
        self.server_thread = None
    
    def start(self):
        """Start the pattern matching microservice"""
        self.server = HTTPServer((self.host, self.port), PatternHTTPHandler)
        self.server.pattern_matcher = self.pattern_matcher
        
        print(f"Starting Pattern service on {self.host}:{self.port}")
        
        # Run server in separate thread
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.daemon = True
        self.server_thread.start()
        
        return self
    
    def stop(self):
        """Stop the pattern matching microservice"""
        if self.server:
            self.server.shutdown()
            self.server.server_close()
            print("Pattern service stopped")
    
    def get_pattern_matcher(self):
        """Get the underlying PatternMatcher instance"""
        return self.pattern_matcher
    
    def is_running(self):
        """Check if service is running"""
        return self.server is not None and self.server_thread.is_alive()


def main():
    """Run Pattern microservice standalone"""
    service = PatternService()
    
    try:
        service.start()
        print("Pattern service is running. Press Ctrl+C to stop.")
        
        # Keep main thread alive
        while True:
            pass
            
    except KeyboardInterrupt:
        print("\nShutting down...")
        service.stop()


if __name__ == "__main__":
    main()