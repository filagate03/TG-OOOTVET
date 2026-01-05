"""Content sender service for sending funnel steps and broadcasts."""
import os
import sqlite3
from typing import List, Optional
from aiogram import Bot
from aiogram.types import FSInputFile, InputMediaPhoto, InputMediaVideo, InlineKeyboardMarkup, InlineKeyboardButton


# Get absolute path to media directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MEDIA_DIR = os.path.join(BASE_DIR, "media")


class ContentSender:
    """Service for sending content to users."""
    
    def __init__(self, bot: Bot):
        self.bot = bot
    
    def get_media_files(self, step_id: int) -> List[dict]:
        """Get media files for a funnel step."""
        db_path = os.path.join(BASE_DIR, 'bot.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT mf.id, mf.project_id, mf.filename, mf.original_name, mf.file_type, mf.telegram_file_id
            FROM media_files mf
            JOIN funnel_media_association fma ON mf.id = fma.media_file_id
            WHERE fma.funnel_step_id = ?
        """, (step_id,))
        files = cursor.fetchall()
        conn.close()
        
        return [
            {
                "id": f[0],
                "project_id": f[1],
                "filename": f[2],
                "original_name": f[3],
                "file_type": f[4],
                "telegram_file_id": f[5]
            }
            for f in files
        ]
    
    def get_broadcast_media_files(self, broadcast_id: int) -> List[dict]:
        """Get media files for a broadcast."""
        db_path = os.path.join(BASE_DIR, 'bot.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT mf.id, mf.project_id, mf.filename, mf.original_name, mf.file_type, mf.telegram_file_id
            FROM media_files mf
            JOIN broadcast_media_association bma ON mf.id = bma.media_file_id
            WHERE bma.broadcast_id = ?
        """, (broadcast_id,))
        files = cursor.fetchall()
        conn.close()
        
        return [
            {
                "id": f[0],
                "project_id": f[1],
                "filename": f[2],
                "original_name": f[3],
                "file_type": f[4],
                "telegram_file_id": f[5]
            }
            for f in files
        ]
    
    def get_buttons(self, step_id: int) -> Optional[List[dict]]:
        """Get buttons for a funnel step."""
        db_path = os.path.join(BASE_DIR, 'bot.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT buttons FROM funnel_steps WHERE id = ?", (step_id,))
        result = cursor.fetchone()
        conn.close()
        
        if result and result[0]:
            import json
            try:
                return json.loads(result[0]) if isinstance(result[0], str) else result[0]
            except:
                return None
        return None
    
    def build_keyboard(self, buttons: List[dict], step_id: int) -> Optional[InlineKeyboardMarkup]:
        """Build InlineKeyboardMarkup from buttons config."""
        if not buttons:
            return None
        
        # Group buttons by row
        rows = {}
        for btn in buttons:
            row_num = btn.get('row', 0)
            if row_num not in rows:
                rows[row_num] = []
            
            if btn['action'] == 'url':
                rows[row_num].append(InlineKeyboardButton(
                    text=btn['text'],
                    url=btn['value']
                ))
            else:  # callback
                rows[row_num].append(InlineKeyboardButton(
                    text=btn['text'],
                    callback_data=f"btn_{step_id}_{len(rows[row_num])}"
                ))
        
        # Build keyboard rows
        keyboard = []
        for row_num in sorted(rows.keys()):
            keyboard.append(rows[row_num])
        
        return InlineKeyboardMarkup(inline_keyboard=keyboard) if keyboard else None
    
    def update_telegram_file_id(self, media_id: int, file_id: str):
        """Update telegram_file_id after first upload."""
        db_path = os.path.join(BASE_DIR, 'bot.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE media_files SET telegram_file_id = ? WHERE id = ?",
            (file_id, media_id)
        )
        conn.commit()
        conn.close()
    
    def get_file_path(self, project_id: int, filename: str) -> str:
        """Get full path to media file."""
        return os.path.join(MEDIA_DIR, str(project_id), filename)
    
    async def send_funnel_step(self, user_telegram_id: int, step: dict) -> bool:
        """Send funnel step content to a user."""
        try:
            content_type = step["content_type"]
            content_text = step.get("content_text") or ""
            step_id = step["id"]
            project_id = step["project_id"]
            
            print(f"[SEND] Sending step {step['step_number']} to {user_telegram_id}: type={content_type}")
            
            # Get buttons for this step
            buttons = self.get_buttons(step_id)
            keyboard = self.build_keyboard(buttons, step_id) if buttons else None
            
            if content_type == "text":
                if content_text:
                    await self.bot.send_message(
                        user_telegram_id, 
                        content_text,
                        reply_markup=keyboard
                    )
                else:
                    print(f"[WARN] Step {step_id} has no text content")
                    return False
            
            elif content_type == "photo":
                media_files = self.get_media_files(step_id)
                print(f"[MEDIA] Found {len(media_files)} media files for step {step_id}")
                
                if media_files:
                    media = media_files[0]
                    file_id = media["telegram_file_id"]
                    
                    if file_id:
                        print(f"[MEDIA] Using cached file_id")
                        await self.bot.send_photo(
                            user_telegram_id, 
                            file_id, 
                            caption=content_text or None,
                            reply_markup=keyboard
                        )
                    else:
                        file_path = self.get_file_path(media["project_id"], media["filename"])
                        print(f"[MEDIA] File path: {file_path}")
                        print(f"[MEDIA] File exists: {os.path.exists(file_path)}")
                        
                        if os.path.exists(file_path):
                            msg = await self.bot.send_photo(
                                user_telegram_id, 
                                FSInputFile(file_path),
                                caption=content_text or None,
                                reply_markup=keyboard
                            )
                            self.update_telegram_file_id(media["id"], msg.photo[-1].file_id)
                            print(f"[OK] Photo sent and cached")
                        else:
                            print(f"[X] File not found: {file_path}")
                            if content_text:
                                await self.bot.send_message(
                                    user_telegram_id, 
                                    content_text,
                                    reply_markup=keyboard
                                )
                else:
                    if content_text:
                        await self.bot.send_message(
                            user_telegram_id, 
                            content_text,
                            reply_markup=keyboard
                        )
            
            elif content_type == "video":
                media_files = self.get_media_files(step_id)
                print(f"[VIDEO] Found {len(media_files)} media files for video step {step_id}")
                
                if media_files:
                    media = media_files[0]
                    file_id = media["telegram_file_id"]
                    
                    if file_id:
                        print(f"[VIDEO] Using cached file_id")
                        await self.bot.send_video(
                            user_telegram_id, 
                            file_id, 
                            caption=content_text or None,
                            reply_markup=keyboard
                        )
                    else:
                        file_path = self.get_file_path(media["project_id"], media["filename"])
                        print(f"[VIDEO] File path: {file_path}")
                        print(f"[VIDEO] File exists: {os.path.exists(file_path)}")
                        
                        if os.path.exists(file_path):
                            msg = await self.bot.send_video(
                                user_telegram_id,
                                FSInputFile(file_path),
                                caption=content_text or None,
                                reply_markup=keyboard
                            )
                            self.update_telegram_file_id(media["id"], msg.video.file_id)
                            print(f"[OK] Video sent and cached")
                        else:
                            print(f"[X] Video file not found: {file_path}")
                            if content_text:
                                await self.bot.send_message(
                                    user_telegram_id, 
                                    content_text,
                                    reply_markup=keyboard
                                )
                else:
                    print(f"[WARN] No media files for video step {step_id}")
                    if content_text:
                        await self.bot.send_message(
                            user_telegram_id, 
                            content_text,
                            reply_markup=keyboard
                        )
            
            elif content_type == "album":
                media_files = self.get_media_files(step_id)
                print(f"[ALBUM] Found {len(media_files)} media files for album step {step_id}")
                
                if media_files:
                    media_group = []
                    for i, media in enumerate(media_files):
                        file_id = media["telegram_file_id"]
                        caption = content_text if i == 0 else None
                        
                        if file_id:
                            if media["file_type"] == "photo":
                                media_group.append(InputMediaPhoto(media=file_id, caption=caption))
                            else:
                                media_group.append(InputMediaVideo(media=file_id, caption=caption))
                        else:
                            file_path = self.get_file_path(media["project_id"], media["filename"])
                            if os.path.exists(file_path):
                                if media["file_type"] == "photo":
                                    media_group.append(InputMediaPhoto(
                                        media=FSInputFile(file_path),
                                        caption=caption
                                    ))
                                else:
                                    media_group.append(InputMediaVideo(
                                        media=FSInputFile(file_path),
                                        caption=caption
                                    ))
                    
                    if media_group:
                        messages = await self.bot.send_media_group(user_telegram_id, media_group)
                        for i, msg in enumerate(messages):
                            if i < len(media_files):
                                media = media_files[i]
                                if not media["telegram_file_id"]:
                                    if msg.photo:
                                        self.update_telegram_file_id(media["id"], msg.photo[-1].file_id)
                                    elif msg.video:
                                        self.update_telegram_file_id(media["id"], msg.video.file_id)
                        print(f"[OK] Album sent with {len(media_group)} items")
                        
                        # Send buttons separately for albums
                        if keyboard:
                            await self.bot.send_message(
                                user_telegram_id,
                                "⬇️ Выберите действие:",
                                reply_markup=keyboard
                            )
                else:
                    if content_text:
                        await self.bot.send_message(
                            user_telegram_id, 
                            content_text,
                            reply_markup=keyboard
                        )
            
            return True
        
        except Exception as e:
            print(f"[X] Error sending to {user_telegram_id}: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    async def send_broadcast(self, broadcast: dict, users: List[dict]) -> int:
        """Send broadcast to multiple users. Returns count of successful sends."""
        sent_count = 0
        
        for user in users:
            try:
                content_type = broadcast.get("content_type", "text")
                content_text = broadcast.get("content_text") or ""
                broadcast_id = broadcast.get("id")
                
                if content_type == "text":
                    if content_text:
                        await self.bot.send_message(user["telegram_id"], content_text)
                        sent_count += 1
                
                elif content_type == "photo":
                    media_files = self.get_broadcast_media_files(broadcast_id)
                    if media_files:
                        media = media_files[0]
                        file_id = media["telegram_file_id"]
                        if file_id:
                            await self.bot.send_photo(user["telegram_id"], file_id, caption=content_text or None)
                            sent_count += 1
                        else:
                            file_path = self.get_file_path(media["project_id"], media["filename"])
                            if os.path.exists(file_path):
                                msg = await self.bot.send_photo(user["telegram_id"], FSInputFile(file_path), caption=content_text or None)
                                self.update_telegram_file_id(media["id"], msg.photo[-1].file_id)
                                sent_count += 1
                            elif content_text:
                                await self.bot.send_message(user["telegram_id"], content_text)
                                sent_count += 1
                    elif content_text:
                        await self.bot.send_message(user["telegram_id"], content_text)
                        sent_count += 1
                
                elif content_type == "video":
                    media_files = self.get_broadcast_media_files(broadcast_id)
                    if media_files:
                        media = media_files[0]
                        file_id = media["telegram_file_id"]
                        if file_id:
                            await self.bot.send_video(user["telegram_id"], file_id, caption=content_text or None)
                            sent_count += 1
                        else:
                            file_path = self.get_file_path(media["project_id"], media["filename"])
                            if os.path.exists(file_path):
                                msg = await self.bot.send_video(user["telegram_id"], FSInputFile(file_path), caption=content_text or None)
                                self.update_telegram_file_id(media["id"], msg.video.file_id)
                                sent_count += 1
                            elif content_text:
                                await self.bot.send_message(user["telegram_id"], content_text)
                                sent_count += 1
                    elif content_text:
                        await self.bot.send_message(user["telegram_id"], content_text)
                        sent_count += 1
                
                elif content_type == "album":
                    media_files = self.get_broadcast_media_files(broadcast_id)
                    if media_files:
                        media_group = []
                        for i, media in enumerate(media_files):
                            file_id = media["telegram_file_id"]
                            caption = content_text if i == 0 else None
                            if file_id:
                                if media["file_type"] == "photo":
                                    media_group.append(InputMediaPhoto(media=file_id, caption=caption))
                                else:
                                    media_group.append(InputMediaVideo(media=file_id, caption=caption))
                            else:
                                file_path = self.get_file_path(media["project_id"], media["filename"])
                                if os.path.exists(file_path):
                                    if media["file_type"] == "photo":
                                        media_group.append(InputMediaPhoto(media=FSInputFile(file_path), caption=caption))
                                    else:
                                        media_group.append(InputMediaVideo(media=FSInputFile(file_path), caption=caption))
                        
                        if media_group:
                            messages = await self.bot.send_media_group(user["telegram_id"], media_group)
                            for i, msg in enumerate(messages):
                                if i < len(media_files):
                                    media = media_files[i]
                                    if not media["telegram_file_id"]:
                                        if msg.photo:
                                            self.update_telegram_file_id(media["id"], msg.photo[-1].file_id)
                                        elif msg.video:
                                            self.update_telegram_file_id(media["id"], msg.video.file_id)
                            sent_count += 1
                        elif content_text:
                            await self.bot.send_message(user["telegram_id"], content_text)
                            sent_count += 1
                    elif content_text:
                        await self.bot.send_message(user["telegram_id"], content_text)
                        sent_count += 1
                
                else:
                    # Unknown content type, send text only
                    if content_text:
                        await self.bot.send_message(user["telegram_id"], content_text)
                        sent_count += 1
                        
            except Exception as e:
                print(f"[X] Failed to send broadcast to {user['telegram_id']}: {e}")
                import traceback
                traceback.print_exc()
        
        return sent_count
