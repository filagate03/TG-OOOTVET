"""Funnel scheduler service."""
import sqlite3
import os
import asyncio
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot

from bot.services.content_sender import ContentSender


# Get absolute path to database
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(BASE_DIR, 'bot.db')


class FunnelScheduler:
    """Scheduler for processing funnel steps."""
    
    def __init__(self, bot: Bot, project_id: int):
        self.bot = bot
        self.project_id = project_id
        self.content_sender = ContentSender(bot)
        self.scheduler = AsyncIOScheduler()
    
    def start(self):
        """Start the scheduler."""
        self.scheduler.add_job(
            self.process_funnel,
            'interval',
            seconds=5,  # Check every 5 seconds for fast response
            id='funnel_processor',
            replace_existing=True
        )
        self.scheduler.start()
        print("[OK] Funnel scheduler started (checking every 5 seconds)")
    
    def stop(self):
        """Stop the scheduler."""
        try:
            self.scheduler.shutdown(wait=False)
        except:
            pass
    
    def get_active_users(self) -> list:
        """Get all active users for the project."""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, telegram_id, funnel_step, funnel_step_sent_at, created_at
            FROM users
            WHERE project_id = ? AND status = 'ACTIVE'
        """, (self.project_id,))
        users = cursor.fetchall()
        conn.close()
        
        return [
            {
                "id": u[0],
                "telegram_id": u[1],
                "funnel_step": u[2],
                "funnel_step_sent_at": u[3],
                "created_at": u[4]
            }
            for u in users
        ]
    
    def get_next_step(self, current_step: int) -> dict | None:
        """Get the next funnel step for the user.
        For step 0 (new user), look for step 1.
        For other steps, look for current + 1.
        """
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # For new users (step 0), look for step 1
        # For others, look for next step
        next_step_number = 1 if current_step == 0 else current_step + 1
        
        cursor.execute("""
            SELECT id, project_id, step_number, delay_seconds, content_type, content_text
            FROM funnel_steps
            WHERE project_id = ? AND step_number = ?
        """, (self.project_id, next_step_number))
        step = cursor.fetchone()
        conn.close()
        
        if step:
            return {
                "id": step[0],
                "project_id": step[1],
                "step_number": step[2],
                "delay_seconds": step[3],
                "content_type": step[4],
                "content_text": step[5]
            }
        return None
    
    def update_user_step(self, user_id: int, new_step: int):
        """Update user's funnel step."""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute("""
            UPDATE users
            SET funnel_step = ?, funnel_step_sent_at = ?, updated_at = ?
            WHERE id = ?
        """, (new_step, now, now, user_id))
        conn.commit()
        conn.close()
    
    def calculate_delay(self, user: dict, step: dict) -> bool:
        """Check if enough time has passed for the next step."""
        delay_seconds = step["delay_seconds"]
        
        # Determine reference time
        if user["funnel_step"] == 0:
            # First step - use created_at
            reference_time = user["created_at"]
        else:
            # Subsequent steps - use funnel_step_sent_at
            reference_time = user["funnel_step_sent_at"]
        
        if not reference_time:
            reference_time = user["created_at"]
        
        # Parse the reference time
        try:
            if isinstance(reference_time, str):
                ref_dt = datetime.strptime(reference_time, '%Y-%m-%d %H:%M:%S')
            else:
                ref_dt = reference_time
        except:
            ref_dt = datetime.now()
        
        # Calculate elapsed time
        elapsed = (datetime.now() - ref_dt).total_seconds()
        
        return elapsed >= delay_seconds
    
    async def process_funnel(self):
        """Process funnel for all active users."""
        try:
            users = self.get_active_users()
            
            for user in users:
                next_step = self.get_next_step(user["funnel_step"])
                
                if not next_step:
                    # No more steps in funnel
                    continue
                
                # Check if delay has passed
                if self.calculate_delay(user, next_step):
                    # Send the step
                    success = await self.content_sender.send_funnel_step(
                        user["telegram_id"],
                        next_step
                    )
                    
                    if success:
                        # Update user's step
                        self.update_user_step(user["id"], next_step["step_number"])
                        print(f"[OK] Sent step {next_step['step_number']} to user {user['telegram_id']}")
        
        except Exception as e:
            print(f"[X] Error processing funnel: {e}")
            import traceback
            traceback.print_exc()
