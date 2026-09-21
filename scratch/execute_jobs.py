import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import asyncio
from src.scripts.cli_presentation import log_and_print_live_cost_breakdown
from src.services.live_execution_runner import live_runner

async def main():
    print("==================================================================")
    print(" CINEAI STUDIO: SEQUENTIAL LIVE PRODUCTION EXECUTION (OPTION A)  ")
    print("==================================================================")
    
    # 1. Execute Job 1: Swiss Alps Walk
    print("\n>>> EXECUTING JOB 1: Swiss Alps 4K Rainy Walk...")
    res1 = await live_runner.run_job_1_swiss_alps(target_duration=15)
    print("JOB 1 FINISHED!")
    print(f"Master Video: {res1['master_video_path']}")
    print(f"Size: {res1['video_size_bytes']} bytes")
    print(f"Elapsed: {res1['elapsed_seconds']}s")
    log_and_print_live_cost_breakdown(
        job_id=res1["job_id"],
        title=res1["title"],
        itemized_spend=res1["itemized_spend"],
    )
    
    # 2. Execute Job 2: Surrumantadiro Telugu Folk Dance
    print("\n>>> EXECUTING JOB 2: Surrumantadiro Telugu Folk Dance...")
    res2 = await live_runner.run_job_2_surrumantadiro(target_duration=15)
    print("JOB 2 FINISHED!")
    print(f"Master Video: {res2['master_video_path']}")
    print(f"Size: {res2['video_size_bytes']} bytes")
    print(f"Elapsed: {res2['elapsed_seconds']}s")
    log_and_print_live_cost_breakdown(
        job_id=res2["job_id"],
        title=res2["title"],
        itemized_spend=res2["itemized_spend"],
    )
    
    # 3. Save Summary Audit
    audit_file = live_runner.save_spend_audit()
    print(f"\nSpend audit saved to: {audit_file}")
    print("ALL JOBS EXECUTED SUCCESSFULLY!")

asyncio.run(main())
