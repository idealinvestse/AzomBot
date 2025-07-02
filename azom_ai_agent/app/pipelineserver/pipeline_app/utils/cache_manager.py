# Cache manager utilities
import time
from typing import Any, Dict, Optional, TypeVar, Generic, Tuple

T = TypeVar('T')

class CacheManager(Generic[T]):
    """
    Hantering av cache för pipelineservern med TTL-funktionalitet.
    
    Attribut:
        default_ttl (int): Default time-to-live i sekunder för cache-entries
    """
    def __init__(self, default_ttl: int = 3600):
        """
        Initierar en ny cache-hanterare.
        
        Args:
            default_ttl: Default time-to-live i sekunder för cache-entries
        """
        self._cache: Dict[str, Tuple[T, float]] = {}
        self.default_ttl = default_ttl
    
    async def get_cache(self, key: str) -> Optional[T]:
        """
        Hämtar ett värde från cachen om det finns och inte har utgått.
        
        Args:
            key: Nyckeln att hämta värde för
            
        Returns:
            Det cachade värdet eller None om nyckeln saknas eller har utgått
        """
        if key not in self._cache:
            return None
            
        value, expiry = self._cache[key]
        if time.time() > expiry:
            # Utgången cache-entry - ta bort den
            await self.delete_cache(key)
            return None
            
        return value
    
    async def set_cache(self, key: str, value: T, ttl: Optional[int] = None) -> None:
        """
        Sparar ett värde i cachen med angiven TTL.
        
        Args:
            key: Nyckeln att spara värde för
            value: Värdet att cacha
            ttl: Time-to-live i sekunder, använder default_ttl om inte angiven
        """
        expiry = time.time() + (ttl if ttl is not None else self.default_ttl)
        self._cache[key] = (value, expiry)
    
    async def delete_cache(self, key: str) -> bool:
        """
        Tar bort en cache-entry.
        
        Args:
            key: Nyckeln att ta bort
            
        Returns:
            True om nyckeln fanns och togs bort, annars False
        """
        if key in self._cache:
            del self._cache[key]
            return True
        return False
    
    async def clear_all(self) -> None:
        """Rensar alla cache-entries."""
        self._cache.clear()
    
    async def cleanup_expired(self) -> int:
        """
        Rensar utgångna cache-entries.
        
        Returns:
            Antal rensade entries
        """
        now = time.time()
        expired_keys = [k for k, (_, exp) in self._cache.items() if now > exp]
        
        for key in expired_keys:
            del self._cache[key]
            
        return len(expired_keys)
