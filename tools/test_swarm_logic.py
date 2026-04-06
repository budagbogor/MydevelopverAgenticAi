import asyncio
import json
from swarm.queen import QueenCoordinator

async def test_queen_decomposition():
    queen = QueenCoordinator()
    mission = "Buat Landing Page modern untuk Toko Kopi Luwak dengan fitur Keranjang Belanja."
    
    print(f"Testing Mission: {mission}")
    plan = await queen.decompose_task(mission)
    
    print("\n--- QUEEN MASTER PLAN ---")
    print(json.dumps(plan, indent=4))
    
    if plan.get('milestones'):
        print("\n✅ Success: Milestones generated.")
    else:
        print("\n❌ Failed: No milestones generated.")

if __name__ == "__main__":
    asyncio.run(test_queen_decomposition())
