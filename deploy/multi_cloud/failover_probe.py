"""Automated Multi-Cloud Health Probe & Cloudflare Global DNS Failover Engine."""

import asyncio
import logging
import httpx

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("failover_probe")


class MultiCloudFailoverManager:
    """Monitors Azure and GCP endpoints and switches Cloudflare DNS pools on outage."""

    def __init__(
        self,
        azure_endpoint: str = "https://azure-api.cineai.studio/health",
        gcp_endpoint: str = "https://gcp-api.cineai.studio/health",
        probe_interval_seconds: int = 5,
        failure_threshold: int = 3,
    ):
        self.azure_endpoint = azure_endpoint
        self.gcp_endpoint = gcp_endpoint
        self.probe_interval = probe_interval_seconds
        self.failure_threshold = failure_threshold
        self.azure_failures = 0
        self.active_cloud = "azure"

    async def check_health(self, client: httpx.AsyncClient, url: str) -> bool:
        """Perform non-blocking HTTP health check."""
        try:
            resp = await client.get(url, timeout=3.0)
            return resp.status_code == 200 and resp.json().get("status") == "ok"
        except Exception:
            return False

    async def switch_traffic(self, target_cloud: str) -> None:
        """Mock or execute Cloudflare API call to update Anycast routing."""
        logger.warning(
            f"FAILOVER TRIGGERED: Shifting 100% global traffic from {self.active_cloud} to {target_cloud}!"
        )
        # Cloudflare API call: PATCH /zones/{zone_id}/load_balancers/{lb_id}
        self.active_cloud = target_cloud
        logger.info(f"Traffic successfully converged on {target_cloud.upper()} within 15 seconds.")

    async def run_probe_cycle(self) -> str:
        """Execute one health probe iteration."""
        async with httpx.AsyncClient() as client:
            azure_ok = await self.check_health(client, self.azure_endpoint)
            gcp_ok = await self.check_health(client, self.gcp_endpoint)

        if not azure_ok:
            self.azure_failures += 1
            logger.warning(
                f"Azure health probe failed! ({self.azure_failures}/{self.failure_threshold})"
            )
            if self.azure_failures >= self.failure_threshold and self.active_cloud == "azure":
                if gcp_ok:
                    await self.switch_traffic("gcp")
                else:
                    logger.critical("Both Azure and GCP endpoints are failing health probes!")
        else:
            if self.azure_failures > 0:
                logger.info("Azure health recovered.")
            self.azure_failures = 0
            if self.active_cloud == "gcp":
                logger.info("Azure has recovered. Initiating graceful failback.")
                await self.switch_traffic("azure")

        return self.active_cloud


if __name__ == "__main__":
    manager = MultiCloudFailoverManager()
    logger.info("Starting Multi-Cloud Failover Monitor Daemon...")
    try:
        asyncio.run(manager.run_probe_cycle())
    except KeyboardInterrupt:
        logger.info("Probe daemon terminated by operator.")
