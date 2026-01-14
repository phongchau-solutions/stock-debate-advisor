"""
API Client for Stock Debate Advisor - Frontend Integration
This can be ported to TypeScript/React for use in the frontend.
"""

import asyncio
import aiohttp
from typing import Optional, Dict, Any, List
from datetime import datetime


class DebateAdvisorClient:
    """HTTP Client for Stock Debate Advisor API"""
    
    def __init__(self, base_url: str = "http://localhost:8000", timeout: int = 30):
        """
        Initialize the API client
        
        Args:
            base_url: Base URL of the API server
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        """Context manager entry"""
        self.session = aiohttp.ClientSession(timeout=self.timeout)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        if self.session:
            await self.session.close()
    
    async def _request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Make HTTP request
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            **kwargs: Additional request parameters
            
        Returns:
            Response JSON
        """
        if not self.session:
            raise RuntimeError("Client not initialized. Use 'async with' context manager.")
        
        url = f"{self.base_url}{endpoint}"
        
        try:
            async with self.session.request(method, url, **kwargs) as response:
                data = await response.json()
                
                if response.status >= 400:
                    raise APIError(
                        status=response.status,
                        message=data.get("detail", data.get("error", "Unknown error")),
                        data=data
                    )
                
                return data
        except aiohttp.ClientError as e:
            raise APIError(
                status=0,
                message=f"Connection error: {str(e)}"
            )
    
    # Health and Config endpoints
    async def health_check(self) -> Dict[str, Any]:
        """Check API health"""
        return await self._request("GET", "/")
    
    async def get_config(self) -> Dict[str, Any]:
        """Get current configuration"""
        return await self._request("GET", "/api/config")
    
    # Symbol endpoints
    async def get_symbols(self) -> List[str]:
        """Get available stock symbols"""
        response = await self._request("GET", "/api/symbols")
        return response.get("symbols", [])
    
    # Debate endpoints
    async def start_debate(self, symbol: str, rounds: int = 3) -> str:
        """
        Start a new debate
        
        Args:
            symbol: Stock symbol
            rounds: Number of debate rounds
            
        Returns:
            Session ID
        """
        payload = {"symbol": symbol, "rounds": rounds}
        response = await self._request(
            "POST",
            "/api/debate/start",
            json=payload
        )
        return response["session_id"]
    
    async def get_debate_status(self, session_id: str) -> Dict[str, Any]:
        """
        Get debate status
        
        Args:
            session_id: Session ID from start_debate
            
        Returns:
            Status information
        """
        return await self._request("GET", f"/api/debate/status/{session_id}")
    
    async def get_debate_result(self, session_id: str) -> Dict[str, Any]:
        """
        Get debate result
        
        Args:
            session_id: Session ID from start_debate
            
        Returns:
            Complete debate result
        """
        return await self._request("GET", f"/api/debate/result/{session_id}")
    
    async def poll_debate_result(
        self,
        session_id: str,
        poll_interval: int = 2,
        max_wait: int = 300
    ) -> Dict[str, Any]:
        """
        Poll for debate result until completion
        
        Args:
            session_id: Session ID from start_debate
            poll_interval: Polling interval in seconds
            max_wait: Maximum wait time in seconds
            
        Returns:
            Complete debate result
        """
        elapsed = 0
        
        while elapsed < max_wait:
            try:
                result = await self.get_debate_result(session_id)
                if result["status"] in ["completed", "failed"]:
                    return result
            except APIError as e:
                if e.status != 202:  # 202 = still in progress
                    raise
            
            await asyncio.sleep(poll_interval)
            elapsed += poll_interval
        
        raise TimeoutError(f"Debate did not complete within {max_wait} seconds")
    
    # Session endpoints
    async def list_sessions(self) -> List[Dict[str, Any]]:
        """List all debate sessions"""
        response = await self._request("GET", "/api/sessions")
        return response.get("sessions", [])
    
    async def get_session(self, session_id: str) -> Dict[str, Any]:
        """Get session details"""
        return await self._request("GET", f"/api/sessions/{session_id}")
    
    async def delete_session(self, session_id: str) -> None:
        """Delete a session"""
        await self._request("DELETE", f"/api/sessions/{session_id}")


class APIError(Exception):
    """API Error"""
    
    def __init__(self, status: int, message: str, data: Optional[Dict] = None):
        self.status = status
        self.message = message
        self.data = data or {}
        super().__init__(f"API Error {status}: {message}")


# Example usage
async def example_usage():
    """Example of how to use the client"""
    
    async with DebateAdvisorClient() as client:
        # Check health
        health = await client.health_check()
        print(f"✅ API Health: {health['status']}")
        
        # Get available symbols
        symbols = await client.get_symbols()
        print(f"📊 Available symbols: {symbols}")
        
        # Start a debate
        print("\n🎯 Starting debate for MBB...")
        session_id = await client.start_debate("MBB", rounds=3)
        print(f"📝 Session ID: {session_id}")
        
        # Check status
        status = await client.get_debate_status(session_id)
        print(f"📈 Status: {status['status']} (Progress: {status['progress']}%)")
        
        # Poll for result
        print("\n⏳ Waiting for debate to complete...")
        result = await client.poll_debate_result(session_id, poll_interval=2)
        
        # Display result
        print("\n✅ Debate completed!")
        print(f"   Recommendation: {result['verdict']['recommendation']}")
        print(f"   Confidence: {result['verdict']['confidence']}")
        print(f"   Score: {result['verdict']['score']}/10")
        print(f"   Rationale: {result['verdict']['rationale']}")


if __name__ == "__main__":
    asyncio.run(example_usage())
