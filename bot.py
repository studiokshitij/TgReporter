import sqlite3
import telethon
from telethon import TelegramClient
from telethon.errors import FloodWaitError, InviteHashInvalidError, InviteHashExpiredError
from telethon.tl.functions.messages import ReportRequest
from telethon.tl.functions.channels import JoinChannelRequest, LeaveChannelRequest
from telethon.tl.functions.messages import ImportChatInviteRequest, DeleteChatUserRequest
import asyncio
import telebot
from telebot import types
from telethon import types as telethon_types
import time
import os
import random
from datetime import datetime, timedelta
from pyCryptoPayAPI import pyCryptoPayAPI

API_CREDENTIALS = [
    ('24565698', '5a084b434f8505ace703485b9da85040'),
    ('27904162', 'e7cba879b1c643ba77490bf328df5eab'),
    ('23037915', '50f06f5b2223586fde0d1379ea91ebc7'),
    ('29512095', '0b29a7d42fff002856b9bed64f7ec919')
]

TOKEN = "bot_token"

bot_name = "Safest Gram Bot"
bot_logs = -1003557266197
bot_admin = "@KshitijShreshth"
bot_banner_link = "https://i.ibb.co/vvq2sQSk/IMG-20260105-190751-513.jpg"

CRYPTO = "44444:gggg"

ADMINS = [00000]

subscribe_1_day = 1
subscribe_7_days = 7
subscribe_14_days = 14
subscribe_30_days = 18
subscribe_365_days = 120
subscribe_infinity_days = 180

user_states = {}
last_used = {}
active_attacks = {}

def log_to_vps(message):
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        
        with open("/var/log/tg_report_bot.log", "a") as f:
            f.write(log_message)
        
        print(log_message.strip())
    except Exception as e:
        print(f"Failed to log to VPS: {e}")

while True:
    try:
        bot = telebot.TeleBot(TOKEN, parse_mode="HTML")
        crypto = pyCryptoPayAPI(api_token=CRYPTO)
        
        session_folder = 'sessions'
        sessions = [f.replace('.session', '') for f in os.listdir(session_folder) if f.endswith('.session')]

        def check_user_in_db(user_id):
            conn = sqlite3.connect('users.db')
            cursor = conn.cursor()
            cursor.execute('SELECT user_id FROM users WHERE user_id = ?', (user_id,))
            result = cursor.fetchone()
            conn.close()
            return result is not None

        def extract_username_and_message_id(message_url):
            try:
                if '?' in message_url:
                    message_url = message_url.split('?')[0]
                
                if 't.me/' in message_url:
                    path = message_url.split('t.me/')[1]
                else:
                    raise ValueError("Invalid Telegram URL")
                
                parts = path.split('/')
                if len(parts) < 2:
                    raise ValueError("Invalid URL format")
                
                chat_username = parts[-2].replace('@', '')
                try:
                    message_id = int(parts[-1])
                except:
                    raise ValueError("Invalid message ID")
                
                return chat_username, message_id
            except Exception as e:
                raise ValueError(f"Invalid link: {str(e)}")

        def extract_username(username_or_url):
            if 't.me/' in username_or_url:
                return username_or_url.split('t.me/')[1].replace('@', '').split('/')[0]
            else:
                return username_or_url.replace('@', '')

        def get_user_subscription(user_id):
            conn = sqlite3.connect('users.db')
            cursor = conn.cursor()
            cursor.execute("SELECT subscribe FROM users WHERE user_id = ?", (user_id,))
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return datetime.strptime(result[0], "%Y-%m-%d %H:%M:%S")
            return datetime.strptime("1999-01-01 20:00:00", "%Y-%m-%d %H:%M:%S")

        def get_main_menu():
            menu = types.InlineKeyboardMarkup(row_width=2)
            profile = types.InlineKeyboardButton("Profile", callback_data='profile')
            doc = types.InlineKeyboardButton("Documentation", callback_data='docs')
            shop = types.InlineKeyboardButton("Shop", callback_data='shop')
            attack = types.InlineKeyboardButton("Attack", callback_data='attack')
            stats = types.InlineKeyboardButton("Statistics", callback_data='stats')
            menu.add(profile, stats)
            menu.add(doc, shop)
            menu.add(attack)
            return menu

        def get_back_button():
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("Back", callback_data='back'))
            return markup

        attack_markup = types.InlineKeyboardMarkup(row_width=1)
        attack_channel = types.InlineKeyboardButton("Channel Attack", callback_data='attack_channel')
        attack_group = types.InlineKeyboardButton("Group Attack", callback_data='attack_group')
        attack_user = types.InlineKeyboardButton("User Attack", callback_data='attack_user')
        attack_markup.add(attack_channel, attack_group, attack_user)
        attack_markup.add(types.InlineKeyboardButton("Back", callback_data='back'))

        reasons_markup = types.InlineKeyboardMarkup(row_width=2)
        reason_spam = types.InlineKeyboardButton("Spam", callback_data='reason_spam')
        reason_violence = types.InlineKeyboardButton("Violence", callback_data='reason_violence')
        reason_porno = types.InlineKeyboardButton("Pornography", callback_data='reason_porno')
        reason_child = types.InlineKeyboardButton("Child Abuse", callback_data='reason_child')
        reason_drugs = types.InlineKeyboardButton("Illegal Drugs", callback_data='reason_drugs')
        reason_personal = types.InlineKeyboardButton("Personal Details", callback_data='reason_personal')
        reason_mass = types.InlineKeyboardButton("MASS REPORT (All Sessions)", callback_data='reason_mass')
        reasons_markup.add(reason_spam, reason_violence)
        reasons_markup.add(reason_porno, reason_child)
        reasons_markup.add(reason_drugs, reason_personal)
        reasons_markup.add(reason_mass)
        reasons_markup.add(types.InlineKeyboardButton("Back", callback_data='back'))

        shop_markup = types.InlineKeyboardMarkup(row_width=2)
        sub_1 = types.InlineKeyboardButton(f"1 Day - ${subscribe_1_day}", callback_data='sub_1')
        sub_2 = types.InlineKeyboardButton(f"7 Days - ${subscribe_7_days}", callback_data='sub_2')
        sub_3 = types.InlineKeyboardButton(f"14 Days - ${subscribe_14_days}", callback_data='sub_3')
        sub_4 = types.InlineKeyboardButton(f"30 Days - ${subscribe_30_days}", callback_data='sub_4')
        sub_5 = types.InlineKeyboardButton(f"365 Days - ${subscribe_365_days}", callback_data='sub_5')
        sub_6 = types.InlineKeyboardButton(f"Forever - ${subscribe_infinity_days}", callback_data='sub_6')
        shop_markup.add(sub_1, sub_2, sub_3, sub_4, sub_5, sub_6)
        shop_markup.add(types.InlineKeyboardButton("Back", callback_data='back'))

        group_type_markup = types.InlineKeyboardMarkup(row_width=1)
        group_public = types.InlineKeyboardButton("Public Group", callback_data='group_public')
        group_private = types.InlineKeyboardButton("Private Group", callback_data='group_private')
        group_type_markup.add(group_public, group_private)
        group_type_markup.add(types.InlineKeyboardButton("Back", callback_data='back'))

        user_attack_markup = types.InlineKeyboardMarkup(row_width=1)
        user_attack_username = types.InlineKeyboardButton("Report User by Username", callback_data='user_attack_username')
        user_attack_markup.add(user_attack_username)
        user_attack_markup.add(types.InlineKeyboardButton("Back", callback_data='back'))

        admin_markup = types.InlineKeyboardMarkup(row_width=2)
        add_subsribe = types.InlineKeyboardButton("Give Subscription", callback_data='add_subsribe')
        clear_subscribe = types.InlineKeyboardButton("Remove Subscription", callback_data='clear_subscribe')
        send_all = types.InlineKeyboardButton("Broadcast", callback_data='send_all')
        check_stats = types.InlineKeyboardButton("Check Stats", callback_data='check_stats')
        admin_markup.add(add_subsribe, clear_subscribe)
        admin_markup.add(send_all, check_stats)
        admin_markup.add(types.InlineKeyboardButton("Back", callback_data='back'))

        async def report_user_by_username(username, reason_type, user_id, report_count, delay_seconds):
            if user_id in active_attacks:
                bot.send_message(user_id, "<b>You already have an active attack! Wait for it to complete.</b>")
                return
            
            active_attacks[user_id] = True
            
            log_to_vps(f"USER ATTACK STARTED - User: {user_id}, Target: @{username}, Type: {reason_type}, Requested Reports: {report_count}")
            
            conn = sqlite3.connect('users.db')
            cursor = conn.cursor()
            
            valid = 0
            invalid = 0
            flood = 0
            failed = 0
            not_found = 0
            
            reason_mapping = {
                'spam': telethon_types.InputReportReasonSpam(),
                'violence': telethon_types.InputReportReasonViolence(),
                'porno': telethon_types.InputReportReasonPornography(),
                'child': telethon_types.InputReportReasonChildAbuse(),
                'drugs': telethon_types.InputReportReasonIllegalDrugs(),
                'personal': telethon_types.InputReportReasonPersonalDetails(),
            }
            
            if reason_type == 'mass':
                all_reasons = list(reason_mapping.values())
                wait_msg = bot.send_message(user_id, "Please wait, MASS REPORT started...")
                log_to_vps(f"MASS REPORT INITIATED - User: {user_id}, All sessions will loop")
            else:
                all_reasons = [reason_mapping.get(reason_type, telethon_types.InputReportReasonSpam())]
                wait_msg = bot.send_message(user_id, "Please wait, reporting user...")
            
            if report_count and report_count > 800:
                report_count = 800
                bot.send_message(user_id, "<b>Report count limited to 800 (maximum allowed)</b>")
            
            if delay_seconds < 0.1 and user_id not in ADMINS:
                delay_seconds = 0.3
                bot.send_message(user_id, "<b>Delay increased to 0.3s (minimum for users)</b>")
            
            if delay_seconds > 1.5:
                delay_seconds = 1.5
                bot.send_message(user_id, "<b>Delay limited to 1.5s (maximum allowed)</b>")
            
            processed = 0
            total_reports_needed = report_count if report_count else len(sessions)
            sessions_count = len(sessions)
            
            log_to_vps(f"User attack - Total reports needed: {total_reports_needed}, Sessions: {sessions_count}, Loops: {total_reports_needed/sessions_count:.1f}")
            
            for report_index in range(total_reports_needed):
                session_index = report_index % sessions_count
                session = sessions[session_index]
                
                api_id, api_hash = random.choice(API_CREDENTIALS)
                
                if reason_type == 'mass':
                    current_reason = random.choice(all_reasons)
                else:
                    current_reason = all_reasons[0]
                
                try:
                    log_to_vps(f"User attack - Loop {report_index+1}/{total_reports_needed} - Session {session} reporting @{username}")
                    
                    client = TelegramClient(f"sessions/{session}", int(api_id), api_hash)
                    await client.connect()
                    
                    if not await client.is_user_authorized():
                        invalid += 1
                        processed += 1
                        log_to_vps(f"Session {session} - Not authorized")
                        await client.disconnect()
                        continue
                    
                    await client.start()
                    
                    try:
                    
                    
                        
                     
                        try:
                            user = await client.get_entity(username)
                            
                            
                            await client(ReportRequest(
                                peer=user,
                                id=[],  
                                reason=current_reason,
                                message=""
                            ))
                            valid += 1
                            log_to_vps(f"Session {session} - User report {report_index+1} sent successfully")
                            
                        except Exception as user_error:
                            # If direct user report fails, try to find user in common groups
                            not_found += 1
                            log_to_vps(f"Session {session} - User not found or cannot report directly: {str(user_error)}")
                        
                        await asyncio.sleep(delay_seconds)
                        
                    except Exception as e:
                        error_msg = str(e).lower()
                        if "user not found" in error_msg or "could not find" in error_msg or "invalid peer" in error_msg:
                            not_found += 1
                            log_to_vps(f"Session {session} - User not found or cannot report")
                        else:
                            failed += 1
                            log_to_vps(f"Session {session} - Error: {str(e)}")
                    
                    processed += 1
                    await client.disconnect()
                    log_to_vps(f"Session {session} - Disconnected")
                    
                except FloodWaitError as e:
                    flood += 1
                    processed += 1
                    log_to_vps(f"Session {session} - FloodWait: {e.seconds} seconds")
                    await client.disconnect()
                    await asyncio.sleep(e.seconds)
                except Exception as e:
                    invalid += 1
                    processed += 1
                    log_to_vps(f"Session {session} - General error: {str(e)}")
                    await client.disconnect()
                    continue
                
                if processed % 10 == 0:
                    try:
                        bot.edit_message_text(
                            f"<b>USER ATTACK IN PROGRESS</b>\n\n"
                            f"<b>Target:</b> @{username}\n"
                            f"<b>Progress:</b> {processed}/{total_reports_needed} ({processed/total_reports_needed*100:.1f}%)\n"
                            f"<b>Successful:</b> {valid}\n"
                            f"<b>Invalid:</b> {invalid}\n"
                            f"<b>Failed:</b> {failed}\n"
                            f"<b>FloodWait:</b> {flood}\n"
                            f"<b>User Not Found:</b> {not_found}",
                            chat_id=user_id,
                            message_id=wait_msg.message_id,
                            disable_web_page_preview=True
                        )
                    except:
                        pass
            
            try:
                bot.delete_message(user_id, wait_msg.message_id)
            except:
                pass
            
            result_message = f"<b>USER ATTACK COMPLETED!</b>\n\n"
            result_message += f"<b>Target:</b> @{username}\n"
            result_message += f"<b>Requested Reports:</b> <code>{report_count if report_count else 'All'}</code>\n"
            result_message += f"<b>Successful Reports:</b> <code>{valid}</code>\n"
            result_message += f"<b>Invalid Sessions:</b> <code>{invalid}</code>\n"
            result_message += f"<b>Failed Attempts:</b> <code>{failed}</code>\n"
            result_message += f"<b>FloodWait Errors:</b> <code>{flood}</code>\n"
            result_message += f"<b>User Not Found:</b> <code>{not_found}</code>\n"
            result_message += f"<b>Total Sessions Used:</b> <code>{sessions_count}</code>\n"
            result_message += f"<b>Delay Between Reports:</b> <code>{delay_seconds}s</code>\n"
            result_message += f"<b>Loops Completed:</b> <code>{total_reports_needed/sessions_count:.1f}</code>\n\n"
            result_message += f"<b>Cooldown:</b> 8 minutes"
            
            bot.send_message(user_id, result_message, reply_markup=get_back_button())
            
            log_markup = types.InlineKeyboardMarkup()
            user_btn = types.InlineKeyboardButton(f"User: {user_id}", url=f'tg://user?id={user_id}')
            log_markup.add(user_btn)
            
            bot.send_message(
                bot_logs,
                f"<b>USER ATTACK REPORT</b>\n\n"
                f"<b>User ID:</b> <code>{user_id}</code>\n"
                f"<b>Target:</b> @{username}\n"
                f"<b>Type:</b> {'MASS REPORT' if reason_type == 'mass' else reason_type}\n"
                f"<b>Requested:</b> {report_count if report_count else 'All'}\n"
                f"<b>Successful:</b> {valid}\n"
                f"<b>Invalid:</b> {invalid}\n"
                f"<b>Failed:</b> {failed}\n"
                f"<b>FloodWait:</b> {flood}\n"
                f"<b>User Not Found:</b> {not_found}",
                reply_markup=log_markup,
                disable_web_page_preview=True
            )
            
            log_to_vps(f"USER ATTACK COMPLETED - User: {user_id}, Valid: {valid}, Invalid: {invalid}, Failed: {failed}, Flood: {flood}, Not Found: {not_found}")
            
            last_used[user_id] = datetime.now()
            del active_attacks[user_id]
            conn.close()

        async def report_message_with_join(chat_username, message_id, reason_type, user_id, report_count, delay_seconds, private_link=None):
            if user_id in active_attacks:
                bot.send_message(user_id, "<b>You already have an active attack! Wait for it to complete.</b>")
                return
            
            active_attacks[user_id] = True
            
            log_to_vps(f"ATTACK STARTED - User: {user_id}, Target chat: {chat_username}, Message: {message_id}, Type: {reason_type}, Requested Reports: {report_count}, Private: {private_link is not None}")
            
            conn = sqlite3.connect('users.db')
            cursor = conn.cursor()
            
            valid = 0
            invalid = 0
            flood = 0
            failed = 0
            not_joined = 0
            left_groups = 0
            
            reason_mapping = {
                'spam': telethon_types.InputReportReasonSpam(),
                'violence': telethon_types.InputReportReasonViolence(),
                'porno': telethon_types.InputReportReasonPornography(),
                'child': telethon_types.InputReportReasonChildAbuse(),
                'drugs': telethon_types.InputReportReasonIllegalDrugs(),
                'personal': telethon_types.InputReportReasonPersonalDetails(),
            }
            
            if reason_type == 'mass':
                all_reasons = list(reason_mapping.values())
                wait_msg = bot.send_message(user_id, "Please wait, MASS REPORT started...\nStep 1: Sessions joining group...")
                log_to_vps(f"MASS REPORT INITIATED - User: {user_id}, All sessions will loop")
            else:
                all_reasons = [reason_mapping.get(reason_type, telethon_types.InputReportReasonSpam())]
                wait_msg = bot.send_message(user_id, "Please wait, reporting started...\nStep 1: Sessions joining group...")
            
            if report_count and report_count > 800:
                report_count = 800
                bot.send_message(user_id, "<b>Report count limited to 800 (maximum allowed)</b>")
            
            if delay_seconds < 0.1 and user_id not in ADMINS:
                delay_seconds = 0.3
                bot.send_message(user_id, "<b>Delay increased to 0.3s (minimum for users)</b>")
            
            if delay_seconds > 1.5:
                delay_seconds = 1.5
                bot.send_message(user_id, "<b>Delay limited to 1.5s (maximum allowed)</b>")
            
            processed = 0
            total_reports_needed = report_count if report_count else len(sessions)
            sessions_count = len(sessions)
            
            log_to_vps(f"Total reports needed: {total_reports_needed}, Sessions: {sessions_count}, Loops: {total_reports_needed/sessions_count:.1f}")
            
            # Store group entities for each session
            session_groups = {}
            
            # STEP 1: ALL SESSIONS JOIN THE GROUP FIRST (if private)
            if private_link:
                try:
                    bot.edit_message_text(
                        f"<b>STEP 1: JOINING GROUP</b>\n\n"
                        f"<b>Target:</b> Private Group\n"
                        f"<b>Sessions:</b> {sessions_count}\n"
                        f"<b>Status:</b> Starting to join...\n\n"
                        f"<i>Please wait 1-2 minutes for all sessions to join smoothly</i>",
                        chat_id=user_id,
                        message_id=wait_msg.message_id
                    )
                    
                    join_count = 0
                    for session_idx, session in enumerate(sessions):
                        try:
                            api_id, api_hash = random.choice(API_CREDENTIALS)
                            log_to_vps(f"Session {session} joining private group...")
                            
                            client = TelegramClient(f"sessions/{session}", int(api_id), api_hash)
                            await client.connect()
                            
                            if not await client.is_user_authorized():
                                log_to_vps(f"Session {session} - Not authorized for joining")
                                await client.disconnect()
                                continue
                            
                            await client.start()
                            
                            try:
                                if private_link.startswith('https://t.me/+') or private_link.startswith('t.me/+'):
                                    invite_hash = private_link.split('+')[1].split('/')[0]
                                    join_result = await client(ImportChatInviteRequest(hash=invite_hash))
                                    log_to_vps(f"Session {session} - Successfully joined private group via invite hash")
                                elif 'joinchat/' in private_link:
                                    invite_hash = private_link.split('joinchat/')[1].split('/')[0]
                                    join_result = await client(ImportChatInviteRequest(hash=invite_hash))
                                    log_to_vps(f"Session {session} - Successfully joined private group via joinchat")
                                
                                # Get the actual chat entity after joining
                                chat = join_result.chats[0]
                                session_groups[session] = {
                                    'client': client,
                                    'chat': chat,
                                    'api_id': api_id,
                                    'api_hash': api_hash
                                }
                                
                                join_count += 1
                                log_to_vps(f"Session {session} - Joined successfully, chat ID: {chat.id}")
                                
                                # Update progress
                                try:
                                    bot.edit_message_text(
                                        f"<b>STEP 1: JOINING GROUP</b>\n\n"
                                        f"<b>Target:</b> Private Group\n"
                                        f"<b>Sessions Joined:</b> {join_count}/{sessions_count}\n"
                                        f"<b>Status:</b> Joining in progress...\n\n"
                                        f"<i>Please wait 1-2 minutes for all sessions to join smoothly</i>",
                                        chat_id=user_id,
                                        message_id=wait_msg.message_id
                                    )
                                except:
                                    pass
                                
                            except (InviteHashInvalidError, InviteHashExpiredError) as e:
                                not_joined += 1
                                log_to_vps(f"Session {session} - Failed to join: Invalid/expired invite")
                                await client.disconnect()
                            except Exception as e:
                                log_to_vps(f"Session {session} - Join error: {str(e)}")
                                await client.disconnect()
                            
                            # Wait between joins (1-3 seconds)
                            await asyncio.sleep(random.uniform(1, 3))
                            
                        except Exception as e:
                            log_to_vps(f"Session {session} - Error during join process: {str(e)}")
                    
                    # Wait 30 seconds after all joins for smooth operation
                    log_to_vps(f"All sessions joined. Waiting 30 seconds before reporting...")
                    try:
                        bot.edit_message_text(
                            f"<b>STEP 1 COMPLETE!</b>\n\n"
                            f"<b>Sessions Joined:</b> {join_count}/{sessions_count}\n"
                            f"<b>Failed to Join:</b> {not_joined}\n\n"
                            f"<b>STEP 2: Starting reports in 30 seconds...</b>\n"
                            f"<i>Sessions will report, then leave the group</i>",
                            chat_id=user_id,
                            message_id=wait_msg.message_id
                        )
                    except:
                        pass
                    
                    await asyncio.sleep(30)
                    
                except Exception as e:
                    log_to_vps(f"Error in join phase: {str(e)}")
            
            # STEP 2: REPORTING PHASE
            try:
                bot.edit_message_text(
                    f"<b>STEP 2: REPORTING PHASE</b>\n\n"
                    f"<b>Target:</b> t.me/{chat_username}/{message_id}\n"
                    f"<b>Requested Reports:</b> {total_reports_needed}\n"
                    f"<b>Status:</b> Starting reports...",
                    chat_id=user_id,
                    message_id=wait_msg.message_id
                )
            except:
                pass
            
            for report_index in range(total_reports_needed):
                session_index = report_index % sessions_count
                session = sessions[session_index]
                
                if reason_type == 'mass':
                    current_reason = random.choice(all_reasons)
                else:
                    current_reason = all_reasons[0]
                
                try:
                    log_to_vps(f"Loop {report_index+1}/{total_reports_needed} - Session {session} reporting")
                    
                    # Check if session already has active client (from join phase)
                    if session in session_groups:
                        client = session_groups[session]['client']
                        chat = session_groups[session]['chat']
                        api_id = session_groups[session]['api_id']
                        api_hash = session_groups[session]['api_hash']
                        
                        # Reconnect if needed
                        if not client.is_connected():
                            client = TelegramClient(f"sessions/{session}", int(api_id), api_hash)
                            await client.connect()
                            await client.start()
                    else:
                        # Create new client for this session
                        api_id, api_hash = random.choice(API_CREDENTIALS)
                        client = TelegramClient(f"sessions/{session}", int(api_id), api_hash)
                        await client.connect()
                        
                        if not await client.is_user_authorized():
                            invalid += 1
                            processed += 1
                            log_to_vps(f"Session {session} - Not authorized")
                            await client.disconnect()
                            continue
                        
                        await client.start()
                        
 
                        try:
                            chat = await client.get_entity(chat_username)
                        except Exception as e:
                            failed += 1
                            processed += 1
                            log_to_vps(f"Session {session} - Could not get entity: {str(e)}")
                            await client.disconnect()
                            continue
                    
                    try:
                        
                        await client(ReportRequest(
                            peer=chat,
                            id=[message_id],
                            reason=current_reason,
                            message=""
                        ))
                        valid += 1
                        log_to_vps(f"Session {session} - Report {report_index+1} sent successfully")
                        
                        
                        if session not in session_groups:
                            session_groups[session] = {
                                'client': client,
                                'chat': chat,
                                'api_id': api_id,
                                'api_hash': api_hash
                            }
                        
                        await asyncio.sleep(delay_seconds)
                        
                    except Exception as e:
                        error_msg = str(e).lower()
                        if "chat not found" in error_msg or "could not find" in error_msg or "cannot find any entity" in error_msg:
                            failed += 1
                            log_to_vps(f"Session {session} - Chat not found: {str(e)}")
                        else:
                            invalid += 1
                            log_to_vps(f"Session {session} - Report error: {str(e)}")
                    
                    processed += 1
                    
                    
                    
                except FloodWaitError as e:
                    flood += 1
                    processed += 1
                    log_to_vps(f"Session {session} - FloodWait: {e.seconds} seconds")
                    await asyncio.sleep(e.seconds)
                except Exception as e:
                    invalid += 1
                    processed += 1
                    log_to_vps(f"Session {session} - General error: {str(e)}")
                
           
                if processed % 10 == 0:
                    try:
                        bot.edit_message_text(
                            f"<b>STEP 2: REPORTING PHASE</b>\n\n"
                            f"<b>Target:</b> t.me/{chat_username}/{message_id}\n"
                            f"<b>Progress:</b> {processed}/{total_reports_needed} ({processed/total_reports_needed*100:.1f}%)\n"
                            f"<b>Successful:</b> {valid}\n"
                            f"<b>Invalid:</b> {invalid}\n"
                            f"<b>Failed:</b> {failed}\n"
                            f"<b>FloodWait:</b> {flood}\n"
                            f"<b>Not Joined:</b> {not_joined}",
                            chat_id=user_id,
                            message_id=wait_msg.message_id,
                            disable_web_page_preview=True
                        )
                    except:
                        pass
            
  
            if private_link and session_groups:
                try:
                    bot.edit_message_text(
                        f"<b>STEP 3: LEAVING GROUPS</b>\n\n"
                        f"<b>Reports Completed!</b>\n"
                        f"<b>Sessions Leaving:</b> {len(session_groups)}\n"
                        f"<b>Status:</b> Sessions leaving the group...",
                        chat_id=user_id,
                        message_id=wait_msg.message_id
                    )
                    
                    for session, data in session_groups.items():
                        try:
                            client = data['client']
                            chat = data['chat']
                            
                            if client.is_connected():
                                try:
                                    # Leave the group/channel
                                    if hasattr(chat, 'channel') or hasattr(chat, 'megagroup'):
                                        await client(LeaveChannelRequest(channel=chat))
                                    else:
                                        await client(DeleteChatUserRequest(
                                            chat_id=chat.id,
                                            user_id=await client.get_me(),
                                            revoke_history=True
                                        ))
                                    
                                    left_groups += 1
                                    log_to_vps(f"Session {session} - Left group successfully")
                                except Exception as e:
                                    log_to_vps(f"Session {session} - Error leaving group: {str(e)}")
                            
                            await client.disconnect()
                            log_to_vps(f"Session {session} - Disconnected")
                            
                        except Exception as e:
                            log_to_vps(f"Session {session} - Error in leave process: {str(e)}")
                            try:
                                await client.disconnect()
                            except:
                                pass
                    
                    log_to_vps(f"Leave phase complete: {left_groups} sessions left the group")
                    
                except Exception as e:
                    log_to_vps(f"Error in leave phase: {str(e)}")
            
            
            for session, data in session_groups.items():
                try:
                    if 'client' in data and data['client'].is_connected():
                        await data['client'].disconnect()
                except:
                    pass
            
            try:
                bot.delete_message(user_id, wait_msg.message_id)
            except:
                pass
            
            
            result_message = ""
            if reason_type == 'mass':
                result_message = f"<b>MASS REPORT COMPLETED!</b>\n\n"
            else:
                result_message = f"<b>ATTACK COMPLETED!</b>\n\n"
            
            result_message += f"<b>Target:</b> t.me/{chat_username}/{message_id}\n"
            result_message += f"<b>Requested Reports:</b> <code>{report_count if report_count else 'All'}</code>\n"
            result_message += f"<b>Successful Reports:</b> <code>{valid}</code>\n"
            result_message += f"<b>Invalid Sessions:</b> <code>{invalid}</code>\n"
            result_message += f"<b>Failed Attempts:</b> <code>{failed}</code>\n"
            result_message += f"<b>FloodWait Errors:</b> <code>{flood}</code>\n"
            
            if private_link:
                result_message += f"<b>Failed to Join:</b> <code>{not_joined}</code>\n"
                result_message += f"<b>Sessions Left Group:</b> <code>{left_groups}</code>\n"
            
            result_message += f"<b>Total Sessions Used:</b> <code>{sessions_count}</code>\n"
            result_message += f"<b>Delay Between Reports:</b> <code>{delay_seconds}s</code>\n"
            result_message += f"<b>Loops Completed:</b> <code>{total_reports_needed/sessions_count:.1f}</code>\n\n"
            
            if reason_type == 'mass':
                result_message += f"<b>Cooldown:</b> 10 minutes"
            else:
                result_message += f"<b>Cooldown:</b> 8 minutes"
            
            bot.send_message(user_id, result_message, reply_markup=get_back_button())
            
            # Send to log channel
            log_markup = types.InlineKeyboardMarkup()
            user_btn = types.InlineKeyboardButton(f"User: {user_id}", url=f'tg://user?id={user_id}')
            log_markup.add(user_btn)
            
            log_message = f"<b>ATTACK REPORT</b>\n\n"
            log_message += f"<b>User ID:</b> <code>{user_id}</code>\n"
            log_message += f"<b>Target:</b> t.me/{chat_username}/{message_id}\n"
            log_message += f"<b>Type:</b> {'MASS REPORT' if reason_type == 'mass' else reason_type}\n"
            log_message += f"<b>Requested:</b> {report_count if report_count else 'All'}\n"
            log_message += f"<b>Successful:</b> {valid}\n"
            log_message += f"<b>Invalid:</b> {invalid}\n"
            log_message += f"<b>Failed:</b> {failed}\n"
            log_message += f"<b>FloodWait:</b> {flood}\n"
            if private_link:
                log_message += f"<b>Failed to Join:</b> {not_joined}\n"
                log_message += f"<b>Sessions Left:</b> {left_groups}"
            
            bot.send_message(
                bot_logs,
                log_message,
                reply_markup=log_markup,
                disable_web_page_preview=True
            )
            
            log_to_vps(f"ATTACK COMPLETED - User: {user_id}, Valid: {valid}, Invalid: {invalid}, Failed: {failed}, Flood: {flood}")
            
            last_used[user_id] = datetime.now()
            del active_attacks[user_id]
            conn.close()

        @bot.message_handler(commands=['start'])
        def welcome(message):
            user_id = message.chat.id
            
            conn = sqlite3.connect("users.db")
            cursor = conn.cursor()
            cursor.execute("""CREATE TABLE IF NOT EXISTS users(
                user_id BIGINT,
                subscribe DATETIME
            )""")
            
            cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
            data = cursor.fetchone()
            
            if data is None:
                cursor.execute("INSERT INTO users VALUES(?, ?);", (user_id, "1999-01-01 20:00:00"))
                conn.commit()
                welcome_msg = f"<b>Welcome to {bot_name}!</b>\n\nYour account has been created."
            else:
                welcome_msg = f"<b>Welcome back to {bot_name}!</b>"
            
            conn.close()
            
            try:
                bot.send_photo(
                    user_id,
                    bot_banner_link,
                    caption=f"{welcome_msg}\n\n"
                           f"<b>Powerful Telegram Report Bot</b>\n\n"
                           f"<b>Admin:</b> {bot_admin}\n"
                           f"<b>Active Sessions:</b> {len(sessions)}\n\n"
                           f"<b>Select an option below:</b>",
                    reply_markup=get_main_menu()
                )
            except:
                bot.send_message(
                    user_id,
                    f"{welcome_msg}\n\n"
                    f"<b>Powerful Telegram Report Bot</b>\n\n"
                    f"<b>Admin:</b> {bot_admin}\n"
                    f"<b>Active Sessions:</b> {len(sessions)}\n\n"
                    f"<b>Select an option below:</b>",
                    reply_markup=get_main_menu()
                )

        @bot.message_handler(commands=['admin'])
        def admin_command(message):
            if message.chat.id in ADMINS:
                bot.send_message(
                    message.chat.id,
                    "<b>ADMINISTRATOR PANEL</b>\n\n"
                    "Select an option below:",
                    reply_markup=admin_markup
                )
            else:
                bot.send_message(message.chat.id, "<b>Access denied. Admin only.</b>")

        @bot.message_handler(commands=['stats'])
        def stats_command(message):
            user_id = message.chat.id
            subscription = get_user_subscription(user_id)
            remaining = subscription - datetime.now()
            days_remaining = remaining.days if remaining.days > 0 else 0
            
            bot.send_message(
                user_id,
                f"<b>BOT STATISTICS</b>\n\n"
                f"<b>Active Sessions:</b> {len(sessions)}\n"
                f"<b>Max Reports:</b> 800\n"
                f"<b>Min Delay:</b> 0.3s (users), 0.1s (admins)\n"
                f"<b>Cooldown:</b> 8 min (normal), 10 min (if active)\n\n"
                f"<b>YOUR STATS</b>\n"
                f"<b>ID:</b> <code>{user_id}</code>\n"
                f"<b>Subscription:</b> {'Active' if subscription > datetime.now() else 'Expired'}\n"
                f"<b>Days Left:</b> {days_remaining}",
                reply_markup=get_back_button()
            )

        @bot.callback_query_handler(func=lambda call: True)
        def callback_handler(call):
            try:
                user_id = call.from_user.id
                
                if call.data == 'back':
                    try:
                        bot.edit_message_caption(
                            chat_id=call.message.chat.id,
                            message_id=call.message.message_id,
                            caption=f"<b>Welcome to {bot_name}!</b>\n\n"
                                   f"<b>Powerful Telegram Report Bot</b>\n\n"
                                   f"<b>Admin:</b> {bot_admin}\n"
                                   f"<b>Active Sessions:</b> {len(sessions)}\n\n"
                                   f"<b>Select an option below:</b>",
                            reply_markup=get_main_menu()
                        )
                    except:
                        bot.edit_message_text(
                            f"<b>Welcome to {bot_name}!</b>\n\n"
                            f"<b>Powerful Telegram Report Bot</b>\n\n"
                            f"<b>Admin:</b> {bot_admin}\n"
                            f"<b>Active Sessions:</b> {len(sessions)}\n\n"
                            f"<b>Select an option below:</b>",
                            chat_id=call.message.chat.id,
                            message_id=call.message.message_id,
                            reply_markup=get_main_menu()
                        )
                    return
                
                elif call.data == 'profile':
                    subscription = get_user_subscription(user_id)
                    remaining = subscription - datetime.now()
                    days_remaining = remaining.days if remaining.days > 0 else 0
                    
                    try:
                        bot.edit_message_caption(
                            chat_id=call.message.chat.id,
                            message_id=call.message.message_id,
                            caption=f"<b>USER PROFILE</b>\n\n"
                                   f"<b>ID:</b> <code>{user_id}</code>\n"
                                   f"<b>Subscription Until:</b> <code>{subscription}</code>\n"
                                   f"<b>Days Remaining:</b> <code>{days_remaining}</code>\n"
                                   f"<b>Active Sessions:</b> <code>{len(sessions)}</code>\n\n"
                                   f"<b>Status:</b> {'Active' if subscription > datetime.now() else 'Expired'}\n"
                                   f"<b>Bot Status:</b> Online",
                            reply_markup=get_back_button()
                        )
                    except:
                        bot.edit_message_text(
                            f"<b>USER PROFILE</b>\n\n"
                            f"<b>ID:</b> <code>{user_id}</code>\n"
                            f"<b>Subscription Until:</b> <code>{subscription}</code>\n"
                            f"<b>Days Remaining:</b> <code>{days_remaining}</code>\n"
                            f"<b>Active Sessions:</b> <code>{len(sessions)}</code>\n\n"
                            f"<b>Status:</b> {'Active' if subscription > datetime.now() else 'Expired'}\n"
                            f"<b>Bot Status:</b> Online",
                            chat_id=call.message.chat.id,
                            message_id=call.message.message_id,
                            reply_markup=get_back_button()
                        )
                
                elif call.data == 'stats':
                    subscription = get_user_subscription(user_id)
                    remaining = subscription - datetime.now()
                    days_remaining = remaining.days if remaining.days > 0 else 0
                    
                    try:
                        bot.edit_message_caption(
                            chat_id=call.message.chat.id,
                            message_id=call.message.message_id,
                            caption=f"<b>BOT STATISTICS</b>\n\n"
                                   f"<b>Active Sessions:</b> {len(sessions)}\n"
                                   f"<b>Max Reports:</b> 800\n"
                                   f"<b>Min Delay:</b> 0.3s (users), 0.1s (admins)\n"
                                   f"<b>Cooldown:</b> 8 min (normal), 10 min (if active)\n\n"
                                   f"<b>YOUR STATS</b>\n"
                                   f"<b>ID:</b> <code>{user_id}</code>\n"
                                   f"<b>Subscription:</b> {'Active' if subscription > datetime.now() else 'Expired'}\n"
                                   f"<b>Days Left:</b> {days_remaining}",
                            reply_markup=get_back_button()
                        )
                    except:
                        bot.edit_message_text(
                            f"<b>BOT STATISTICS</b>\n\n"
                            f"<b>Active Sessions:</b> {len(sessions)}\n"
                            f"<b>Max Reports:</b> 800\n"
                            f"<b>Min Delay:</b> 0.3s (users), 0.1s (admins)\n"
                            f"<b>Cooldown:</b> 8 min (normal), 10 min (if active)\n\n"
                            f"<b>YOUR STATS</b>\n"
                            f"<b>ID:</b> <code>{user_id}</code>\n"
                            f"<b>Subscription:</b> {'Active' if subscription > datetime.now() else 'Expired'}\n"
                            f"<b>Days Left:</b> {days_remaining}",
                            chat_id=call.message.chat.id,
                            message_id=call.message.message_id,
                            reply_markup=get_back_button()
                        )
                
                elif call.data == 'docs':
                    try:
                        bot.edit_message_caption(
                            chat_id=call.message.chat.id,
                            message_id=call.message.message_id,
                            caption=f"<b>DOCUMENTATION</b>\n\n"
                                   f"<b>How to use {bot_name}:</b>\n\n"
                                   f"<b>3-STEP PROCESS:</b>\n\n"
                                   f"1. <b>JOIN PHASE</b> (Private Groups Only)\n"
                                   f"   • All sessions join the group first\n"
                                   f"   • Wait 1-2 minutes for smooth joining\n"
                                   f"   • Wait 30 seconds after all joins\n\n"
                                   f"2. <b>REPORT PHASE</b>\n"
                                   f"   • Sessions report the target message\n"
                                   f"   • Auto-loop: 24 sessions → 800 reports\n"
                                   f"   • Each session reports multiple times\n\n"
                                   f"3. <b>LEAVE PHASE</b> (Private Groups Only)\n"
                                   f"   • All sessions leave the group\n"
                                   f"   • Clean exit after reporting\n\n"
                                   f"<b>ATTACK TYPES:</b>\n"
                                   f"• Channel: Public/private channels\n"
                                   f"• Group: Public/private groups\n"
                                   f"• User: Report by @username\n\n"
                                   f"<b>FEATURES:</b>\n"
                                   f"• Sessions do all work (not bot)\n"
                                   f"• Auto-join private groups\n"
                                   f"• Auto-leave after reporting\n"
                                   f"• Loop system for many reports\n"
                                   f"• VPS logging\n\n"
                                   f"<b>Important:</b>\n"
                                   f"• Subscription required\n"
                                   f"• Respect Telegram rules\n"
                                   f"• Use responsibly",
                            reply_markup=get_back_button()
                        )
                    except:
                        bot.edit_message_text(
                            f"<b>DOCUMENTATION</b>\n\n"
                            f"<b>How to use {bot_name}:</b>\n\n"
                            f"<b>3-STEP PROCESS:</b>\n\n"
                            f"1. <b>JOIN PHASE</b> (Private Groups Only)\n"
                            f"   • All sessions join the group first\n"
                            f"   • Wait 1-2 minutes for smooth joining\n"
                            f"   • Wait 30 seconds after all joins\n\n"
                            f"2. <b>REPORT PHASE</b>\n"
                            f"   • Sessions report the target message\n"
                            f"   • Auto-loop: 24 sessions → 800 reports\n"
                            f"   • Each session reports multiple times\n\n"
                            f"3. <b>LEAVE PHASE</b> (Private Groups Only)\n"
                            f"   • All sessions leave the group\n"
                            f"   • Clean exit after reporting\n\n"
                            f"<b>ATTACK TYPES:</b>\n"
                            f"• Channel: Public/private channels\n"
                            f"• Group: Public/private groups\n"
                            f"• User: Report by @username\n\n"
                            f"<b>FEATURES:</b>\n"
                            f"• Sessions do all work (not bot)\n"
                            f"• Auto-join private groups\n"
                            f"• Auto-leave after reporting\n"
                            f"• Loop system for many reports\n"
                            f"• VPS logging\n\n"
                            f"<b>Important:</b>\n"
                            f"• Subscription required\n"
                            f"• Respect Telegram rules\n"
                            f"• Use responsibly",
                            chat_id=call.message.chat.id,
                            message_id=call.message.message_id,
                            reply_markup=get_back_button()
                        )
                
                elif call.data == 'shop':
                    try:
                        bot.edit_message_caption(
                            chat_id=call.message.chat.id,
                            message_id=call.message.message_id,
                            caption=f"<b>SUBSCRIPTION SHOP</b>\n\n"
                                   f"<b>1 DAY</b> - <code>${subscribe_1_day}</code>\n"
                                   f"<b>7 DAYS</b> - <code>${subscribe_7_days}</code>\n"
                                   f"<b>14 DAYS</b> - <code>${subscribe_14_days}</code>\n"
                                   f"<b>30 DAYS</b> - <code>${subscribe_30_days}</code>\n"
                                   f"<b>365 DAYS</b> - <code>${subscribe_365_days}</code>\n"
                                   f"<b>FOREVER</b> - <code>${subscribe_infinity_days}</code>\n\n"
                                   f"<b>Benefits:</b>\n"
                                   f"• Unlimited attack requests\n"
                                   f"• Priority processing\n"
                                   f"• Access to all features\n"
                                   f"• 24/7 Support\n\n"
                                   f"<b>Contact admin:</b> {bot_admin}",
                            reply_markup=shop_markup
                        )
                    except:
                        bot.edit_message_text(
                            f"<b>SUBSCRIPTION SHOP</b>\n\n"
                            f"<b>1 DAY</b> - <code>${subscribe_1_day}</code>\n"
                            f"<b>7 DAYS</b> - <code>${subscribe_7_days}</code>\n"
                            f"<b>14 DAYS</b> - <code>${subscribe_14_days}</code>\n"
                            f"<b>30 DAYS</b> - <code>${subscribe_30_days}</code>\n"
                            f"<b>365 DAYS</b> - <code>${subscribe_365_days}</code>\n"
                            f"<b>FOREVER</b> - <code>${subscribe_infinity_days}</code>\n\n"
                            f"<b>Benefits:</b>\n"
                            f"• Unlimited attack requests\n"
                            f"• Priority processing\n"
                            f"• Access to all features\n"
                            f"• 24/7 Support\n\n"
                            f"<b>Contact admin:</b> {bot_admin}",
                            chat_id=call.message.chat.id,
                            message_id=call.message.message_id,
                            reply_markup=shop_markup
                        )
                
                elif call.data == 'attack':
                    subscription = get_user_subscription(user_id)
                    
                    if subscription < datetime.now():
                        bot.answer_callback_query(call.id, "Subscription expired! Please renew.", show_alert=True)
                        return
                    
                    if user_id in last_used:
                        time_since = datetime.now() - last_used[user_id]
                        cooldown = 600 if user_id in active_attacks else 480
                        
                        if time_since.total_seconds() < cooldown:
                            remaining = cooldown - time_since.total_seconds()
                            minutes = int(remaining // 60)
                            seconds = int(remaining % 60)
                            bot.answer_callback_query(call.id, f"Cooldown: {minutes}m {seconds}s", show_alert=True)
                            return
                    
                    try:
                        bot.edit_message_caption(
                            chat_id=call.message.chat.id,
                            message_id=call.message.message_id,
                            caption="<b>SELECT ATTACK TYPE</b>\n\n"
                                   "Choose the type of target:",
                            reply_markup=attack_markup
                        )
                    except:
                        bot.edit_message_text(
                            "<b>SELECT ATTACK TYPE</b>\n\n"
                            "Choose the type of target:",
                            chat_id=call.message.chat.id,
                            message_id=call.message.message_id,
                            reply_markup=attack_markup
                        )
                
                elif call.data.startswith('sub_'):
                    sub_type = call.data.split('_')[1]
                    
                    prices = {
                        '1': subscribe_1_day,
                        '2': subscribe_7_days,
                        '3': subscribe_14_days,
                        '4': subscribe_30_days,
                        '5': subscribe_365_days,
                        '6': subscribe_infinity_days
                    }
                    
                    days_map = {
                        '1': '1',
                        '2': '7', 
                        '3': '14',
                        '4': '30',
                        '5': '365',
                        '6': 'Forever'
                    }
                    
                    if sub_type in prices:
                        invoice = crypto.create_invoice(asset='USDT', amount=prices[sub_type])
                        pay_url = invoice['pay_url']
                        invoice_id = invoice['invoice_id']
                        
                        pay_markup = types.InlineKeyboardMarkup(row_width=2)
                        pay_btn = types.InlineKeyboardButton("Pay Now", url=pay_url)
                        check_btn = types.InlineKeyboardButton("Check Payment", 
                            callback_data=f'check_{invoice_id}_{sub_type}_{days_map[sub_type]}')
                        pay_markup.add(pay_btn, check_btn)
                        pay_markup.add(types.InlineKeyboardButton("Back", callback_data='back'))
                        
                        try:
                            bot.edit_message_caption(
                                chat_id=call.message.chat.id,
                                message_id=call.message.message_id,
                                caption=f"<b>PAYMENT REQUEST</b>\n\n"
                                       f"<b>Plan:</b> {days_map[sub_type]} days\n"
                                       f"<b>Amount:</b> <code>${prices[sub_type]}</code>\n\n"
                                       f"<b>Instructions:</b>\n"
                                       f"1. Click 'Pay Now'\n"
                                       f"2. Complete payment\n"
                                       f"3. Click 'Check Payment'\n\n"
                                       f"<b>Note:</b> Payments are processed via CryptoBot",
                                reply_markup=pay_markup
                            )
                        except:
                            bot.edit_message_text(
                                f"<b>PAYMENT REQUEST</b>\n\n"
                                f"<b>Plan:</b> {days_map[sub_type]} days\n"
                                f"<b>Amount:</b> <code>${prices[sub_type]}</code>\n\n"
                                f"<b>Instructions:</b>\n"
                                f"1. Click 'Pay Now'\n"
                                f"2. Complete payment\n"
                                f"3. Click 'Check Payment'\n\n"
                                f"<b>Note:</b> Payments are processed via CryptoBot",
                                chat_id=call.message.chat.id,
                                message_id=call.message.message_id,
                                reply_markup=pay_markup
                            )
                
                elif call.data.startswith('check_'):
                    parts = call.data.split('_')
                    if len(parts) >= 4:
                        invoice_id = parts[1]
                        sub_type = parts[2]
                        days = parts[3]
                        
                        invoice_info = crypto.get_invoices(invoice_ids=invoice_id)
                        
                        if invoice_info['items'][0]['status'] == 'paid':
                            bot.answer_callback_query(call.id, "Payment received! Activating subscription...", show_alert=True)
                            
                            if days == 'Forever':
                                new_date = "2099-12-31 23:59:59"
                            else:
                                days_int = int(days)
                                new_date = (datetime.now() + timedelta(days=days_int)).strftime("%Y-%m-%d %H:%M:%S")
                            
                            conn = sqlite3.connect('users.db')
                            cursor = conn.cursor()
                            cursor.execute("UPDATE users SET subscribe = ? WHERE user_id = ?", (new_date, user_id))
                            conn.commit()
                            conn.close()
                            
                            try:
                                bot.edit_message_caption(
                                    chat_id=call.message.chat.id,
                                    message_id=call.message.message_id,
                                    caption=f"<b>PAYMENT SUCCESSFUL!</b>\n\n"
                                           f"<b>Subscription Activated</b>\n"
                                           f"<b>Valid Until:</b> <code>{new_date}</code>\n"
                                           f"<b>User ID:</b> <code>{user_id}</code>\n\n"
                                           f"<b>Thank you for your purchase!</b>\n"
                                           f"You now have access to all premium features.",
                                    reply_markup=get_back_button()
                                )
                            except:
                                bot.edit_message_text(
                                    f"<b>PAYMENT SUCCESSFUL!</b>\n\n"
                                    f"<b>Subscription Activated</b>\n"
                                    f"<b>Valid Until:</b> <code>{new_date}</code>\n"
                                    f"<b>User ID:</b> <code>{user_id}</code>\n\n"
                                    f"<b>Thank you for your purchase!</b>\n"
                                    f"You now have access to all premium features.",
                                    chat_id=call.message.chat.id,
                                    message_id=call.message.message_id,
                                    reply_markup=get_back_button()
                                )
                            
                            log_markup = types.InlineKeyboardMarkup()
                            user_btn = types.InlineKeyboardButton(f"User: {user_id}", url=f'tg://user?id={user_id}')
                            log_markup.add(user_btn)
                            
                            bot.send_message(
                                bot_logs,
                                f"<b>NEW SUBSCRIPTION</b>\n\n"
                                f"<b>User:</b> <code>{user_id}</code>\n"
                                f"<b>Valid Until:</b> <code>{new_date}</code>\n"
                                f"<b>Plan:</b> {days} days",
                                reply_markup=log_markup
                            )
                        else:
                            bot.answer_callback_query(call.id, "Payment not received yet!", show_alert=True)
                
                elif call.data in ['attack_channel', 'attack_group', 'attack_user']:
                    user_states[user_id] = {'type': call.data}
                    
                    if call.data == 'attack_channel':
                        msg = bot.send_message(
                            call.message.chat.id,
                            "<b>CHANNEL ATTACK</b>\n\n"
                            "Enter link to channel message:\n"
                            "<b>Format:</b> https://t.me/channel_name/message_id\n\n"
                            "<b>Example:</b> https://t.me/sample_channel/12345\n\n"
                            "<b>For private channels:</b> Enter invite link first, then message link"
                        )
                        bot.register_next_step_handler(msg, process_channel_link)
                    
                    elif call.data == 'attack_group':
                        try:
                            bot.edit_message_caption(
                                chat_id=call.message.chat.id,
                                message_id=call.message.message_id,
                                caption="<b>GROUP ATTACK</b>\n\n"
                                       "Select group type:",
                                reply_markup=group_type_markup
                            )
                        except:
                            bot.edit_message_text(
                                "<b>GROUP ATTACK</b>\n\n"
                                "Select group type:",
                                chat_id=call.message.chat.id,
                                message_id=call.message.message_id,
                                reply_markup=group_type_markup
                            )
                    
                    elif call.data == 'attack_user':
                        try:
                            bot.edit_message_caption(
                                chat_id=call.message.chat.id,
                                message_id=call.message.message_id,
                                caption="<b>USER ATTACK</b>\n\n"
                                       "Report user by username:",
                                reply_markup=user_attack_markup
                            )
                        except:
                            bot.edit_message_text(
                                "<b>USER ATTACK</b>\n\n"
                                "Report user by username:",
                                chat_id=call.message.chat.id,
                                message_id=call.message.message_id,
                                reply_markup=user_attack_markup
                            )
                
                elif call.data in ['group_public', 'group_private']:
                    user_states[user_id]['type'] = call.data
                    
                    if call.data == 'group_public':
                        msg = bot.send_message(
                            call.message.chat.id,
                            "<b>PUBLIC GROUP ATTACK</b>\n\n"
                            "Enter link to group message:\n"
                            "<b>Format:</b> https://t.me/group_name/message_id\n\n"
                            "<b>Note:</b> Public groups are easier to target."
                        )
                        bot.register_next_step_handler(msg, process_group_link)
                    
                    elif call.data == 'group_private':
                        msg = bot.send_message(
                            call.message.chat.id,
                            "<b>PRIVATE GROUP ATTACK</b>\n\n"
                            "Enter the private group invite link:\n"
                            "<b>Format:</b> t.me/+invitehash OR t.me/joinchat/invitehash\n\n"
                            "<b>Examples:</b>\n"
                            "• t.me/+AbCdEfGhIjKlMnOp\n"
                            "• t.me/joinchat/AbCdEfGhIjKlMnOp\n\n"
                            "After joining, enter the message link to report."
                        )
                        bot.register_next_step_handler(msg, process_private_group_invite)
                
                elif call.data == 'user_attack_username':
                    user_states[user_id]['type'] = call.data
                    
                    msg = bot.send_message(
                        call.message.chat.id,
                        "<b>REPORT USER BY USERNAME</b>\n\n"
                        "Enter username to report (with @):\n"
                        "<b>Format:</b> @username\n\n"
                        "<b>Example:</b> @username\n\n"
                        "<b>Note:</b> Sessions will report the user directly"
                    )
                    bot.register_next_step_handler(msg, process_user_username)
                
                elif call.data.startswith('reason_'):
                    reason_type = call.data.split('_')[1]
                    user_states[user_id]['reason'] = reason_type
                    
                    if reason_type == 'mass':
                        bot.send_message(
                            user_id,
                            "<b>MASS REPORT SELECTED</b>\n\n"
                            f"<b>Total Sessions:</b> {len(sessions)}\n"
                            "<b>All sessions will loop for maximum impact</b>\n"
                            "<b>Maximum impact guaranteed!</b>\n\n"
                            "<b>Proceed with caution!</b>"
                        )
                    
                    msg = bot.send_message(
                        call.message.chat.id,
                        f"<b>AUTO-LOOP SYSTEM</b>\n\n"
                        f"<b>Sessions will loop to reach requested count</b>\n\n"
                        f"<b>Available Sessions:</b> <code>{len(sessions)}</code>\n"
                        f"<b>Example:</b> 24 sessions + 800 reports = 33.3 loops\n\n"
                        "Enter number of reports to send (1-800):\n"
                        "<b>Leave empty to use all sessions once</b>"
                    )
                    bot.register_next_step_handler(msg, process_report_count)
                
                elif call.data == 'add_subsribe':
                    if user_id not in ADMINS:
                        bot.answer_callback_query(call.id, "Admin access required!", show_alert=True)
                        return
                    msg = bot.send_message(call.message.chat.id, "<b>Enter user ID to give subscription:</b>")
                    bot.register_next_step_handler(msg, add_subscription)
                
                elif call.data == 'clear_subscribe':
                    if user_id not in ADMINS:
                        bot.answer_callback_query(call.id, "Admin access required!", show_alert=True)
                        return
                    msg = bot.send_message(call.message.chat.id, "<b>Enter user ID to remove subscription:</b>")
                    bot.register_next_step_handler(msg, remove_subscription)
                
                elif call.data == 'send_all':
                    if user_id not in ADMINS:
                        bot.answer_callback_query(call.id, "Admin access required!", show_alert=True)
                        return
                    msg = bot.send_message(call.message.chat.id, "<b>Enter broadcast message:</b>")
                    bot.register_next_step_handler(msg, broadcast_message)
                
                elif call.data == 'check_stats':
                    if user_id not in ADMINS:
                        bot.answer_callback_query(call.id, "Admin access required!", show_alert=True)
                        return
                    
                    conn = sqlite3.connect('users.db')
                    cursor = conn.cursor()
                    cursor.execute("SELECT COUNT(*) FROM users")
                    total_users = cursor.fetchone()[0]
                    
                    cursor.execute("SELECT COUNT(*) FROM users WHERE subscribe > datetime('now')")
                    active_users = cursor.fetchone()[0]
                    conn.close()
                    
                    bot.send_message(
                        user_id,
                        f"<b>ADMIN STATISTICS</b>\n\n"
                        f"<b>Total Users:</b> {total_users}\n"
                        f"<b>Active Subscriptions:</b> {active_users}\n"
                        f"<b>Session Pool:</b> {len(sessions)}\n"
                        f"<b>Bot Status:</b> Online",
                        reply_markup=get_back_button()
                    )
                
            except Exception as e:
                print(f"Callback error: {e}")

        def process_channel_link(message):
            user_id = message.from_user.id
            try:
                if 't.me/+' in message.text or 'joinchat/' in message.text:
                    user_states[user_id]['private_link'] = message.text
                    msg = bot.send_message(
                        message.chat.id,
                        "<b>PRIVATE CHANNEL DETECTED</b>\n\n"
                        "Now enter the message link to report:\n"
                        "<b>Format:</b> https://t.me/channel_name/message_id\n\n"
                        "Sessions will join the channel first, then report."
                    )
                    bot.register_next_step_handler(msg, process_private_channel_message)
                else:
                    chat_username, message_id = extract_username_and_message_id(message.text)
                    user_states[user_id]['target'] = {'chat_username': chat_username, 'message_id': message_id}
                    bot.send_message(
                        message.chat.id,
                        "<b>SELECT REPORT REASON</b>\n\n"
                        "Choose the violation reason:",
                        reply_markup=reasons_markup
                    )
            except Exception as e:
                bot.send_message(message.chat.id, f"<b>Error:</b> {str(e)}")

        def process_private_channel_message(message):
            user_id = message.from_user.id
            try:
                chat_username, message_id = extract_username_and_message_id(message.text)
                user_states[user_id]['target'] = {'chat_username': chat_username, 'message_id': message_id}
                bot.send_message(
                    message.chat.id,
                    "<b>SELECT REPORT REASON</b>\n\n"
                    "Choose the violation reason:",
                    reply_markup=reasons_markup
                )
            except Exception as e:
                bot.send_message(message.chat.id, f"<b>Error:</b> {str(e)}")

        def process_group_link(message):
            user_id = message.from_user.id
            try:
                chat_username, message_id = extract_username_and_message_id(message.text)
                user_states[user_id]['target'] = {'chat_username': chat_username, 'message_id': message_id}
                bot.send_message(
                    message.chat.id,
                    "<b>SELECT REPORT REASON</b>\n\n"
                    "Choose the violation reason:",
                    reply_markup=reasons_markup
                )
            except Exception as e:
                bot.send_message(message.chat.id, f"<b>Error:</b> {str(e)}")

        def process_private_group_invite(message):
            user_id = message.from_user.id
            try:
                private_link = message.text.strip()
                user_states[user_id]['private_link'] = private_link
                
                msg = bot.send_message(
                    message.chat.id,
                    "<b>PRIVATE GROUP INVITE SAVED</b>\n\n"
                    "Now enter the message link to report:\n"
                    "<b>Format:</b> https://t.me/group_name/message_id\n\n"
                    "Sessions will join the group first, then report the message."
                )
                bot.register_next_step_handler(msg, process_private_group_message)
            except Exception as e:
                bot.send_message(message.chat.id, f"<b>Error:</b> {str(e)}")

        def process_private_group_message(message):
            user_id = message.from_user.id
            try:
                chat_username, message_id = extract_username_and_message_id(message.text)
                user_states[user_id]['target'] = {'chat_username': chat_username, 'message_id': message_id}
                bot.send_message(
                    message.chat.id,
                    "<b>SELECT REPORT REASON</b>\n\n"
                    "Choose the violation reason:",
                    reply_markup=reasons_markup
                )
            except Exception as e:
                bot.send_message(message.chat.id, f"<b>Error:</b> {str(e)}")

        def process_user_username(message):
            user_id = message.from_user.id
            try:
                username = message.text.strip()
                if not username.startswith('@'):
                    username = '@' + username
                
                user_states[user_id]['target'] = {'username': username}
                bot.send_message(
                    message.chat.id,
                    "<b>SELECT REPORT REASON</b>\n\n"
                    "Choose the violation reason:",
                    reply_markup=reasons_markup
                )
            except Exception as e:
                bot.send_message(message.chat.id, f"<b>Error:</b> {str(e)}")

        def process_report_count(message):
            user_id = message.from_user.id
            try:
                if message.text.strip():
                    report_count = int(message.text)
                    if report_count <= 0:
                        report_count = len(sessions)
                    if report_count > 800:
                        report_count = 800
                        bot.send_message(user_id, "<b>Limited to 800 reports</b>")
                else:
                    report_count = len(sessions)
                
                user_states[user_id]['report_count'] = report_count
                
                msg = bot.send_message(
                    message.chat.id,
                    f"<b>SET DELAY</b>\n\n"
                    f"<b>Requested Reports:</b> <code>{report_count}</code>\n"
                    f"<b>Available Sessions:</b> <code>{len(sessions)}</code>\n"
                    f"<b>Loops Needed:</b> <code>{report_count/len(sessions):.1f} if {report_count} > {len(sessions)}</code>\n\n"
                    "Enter delay between reports (seconds):\n"
                    "<b>Range:</b> 0.1-1.5 seconds\n"
                    "<b>Admin min:</b> 0.1s\n"
                    "<b>User min:</b> 0.3s"
                )
                bot.register_next_step_handler(msg, process_delay)
                    
            except ValueError:
                bot.send_message(message.chat.id, "<b>Enter a valid number!</b>")

        def process_delay(message):
            user_id = message.from_user.id
            
            try:
                delay_seconds = float(message.text.strip())
                
                if delay_seconds < 0.1 and user_id not in ADMINS:
                    delay_seconds = 0.3
                    bot.send_message(user_id, "<b>Delay increased to 0.3s (minimum for users)</b>")
                
                if delay_seconds < 0.1:
                    delay_seconds = 0.1
                
                if delay_seconds > 1.5:
                    delay_seconds = 1.5
                    bot.send_message(user_id, "<b>Delay limited to 1.5s (maximum allowed)</b>")
                
                user_states[user_id]['delay_seconds'] = delay_seconds
                
                state = user_states.get(user_id, {})
                attack_type = state.get('type', '')
                reason_type = state.get('reason', '')
                report_count = state.get('report_count', len(sessions))
                
                if attack_type == 'user_attack_username':
                    target = state.get('target', {})
                    if 'username' in target:
                        bot.send_message(message.chat.id, "<b>LAUNCHING USER ATTACK...</b>")
                        asyncio.run(report_user_by_username(
                            target['username'],
                            reason_type,
                            user_id,
                            report_count,
                            delay_seconds
                        ))
                else:
                    target = state.get('target', {})
                    private_link = state.get('private_link')
                    if 'chat_username' in target and 'message_id' in target:
                        bot.send_message(message.chat.id, "<b>LAUNCHING ATTACK...</b>")
                        asyncio.run(report_message_with_join(
                            target['chat_username'],
                            target['message_id'],
                            reason_type,
                            user_id,
                            report_count,
                            delay_seconds,
                            private_link
                        ))
                
                if user_id in user_states:
                    del user_states[user_id]
                    
            except ValueError:
                bot.send_message(message.chat.id, "<b>Enter a valid number!</b>")

        def add_subscription(message):
            try:
                target_id = int(message.text)
                msg = bot.send_message(message.chat.id, "<b>Enter number of days:</b>")
                bot.register_next_step_handler(msg, lambda m: add_subscription_days(m, target_id))
            except:
                bot.send_message(message.chat.id, "<b>Invalid user ID!</b>")

        def add_subscription_days(message, target_id):
            try:
                days = int(message.text)
                new_date = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S")
                
                conn = sqlite3.connect('users.db')
                cursor = conn.cursor()
                cursor.execute("UPDATE users SET subscribe = ? WHERE user_id = ?", (new_date, target_id))
                conn.commit()
                conn.close()
                
                bot.send_message(message.chat.id, f"<b>Subscription added to user {target_id}</b>\nValid until: {new_date}")
                bot.send_message(target_id, f"<b>Your subscription has been extended!</b>\nValid until: {new_date}")
            except:
                bot.send_message(message.chat.id, "<b>Error adding subscription!</b>")

        def remove_subscription(message):
            try:
                target_id = int(message.text)
                new_date = "1999-01-01 20:00:00"
                
                conn = sqlite3.connect('users.db')
                cursor = conn.cursor()
                cursor.execute("UPDATE users SET subscribe = ? WHERE user_id = ?", (new_date, target_id))
                conn.commit()
                conn.close()
                
                bot.send_message(message.chat.id, f"<b>Subscription removed from user {target_id}</b>")
                bot.send_message(target_id, "<b>Your subscription has been removed!</b>")
            except:
                bot.send_message(message.chat.id, "<b>Error removing subscription!</b>")

        def broadcast_message(message):
            text = message.text
            conn = sqlite3.connect('users.db')
            cursor = conn.cursor()
            users = cursor.execute("SELECT user_id FROM users").fetchall()
            conn.close()
            
            success = 0
            failed = 0
            
            progress_msg = bot.send_message(message.chat.id, f"<b>Broadcasting to {len(users)} users...</b>")
            
            for user in users:
                try:
                    bot.send_message(user[0], text)
                    success += 1
                except:
                    failed += 1
            
            bot.edit_message_text(
                f"<b>BROADCAST COMPLETE</b>\n\n"
                f"<b>Successful:</b> <code>{success}</code>\n"
                f"<b>Failed:</b> <code>{failed}</code>\n"
                f"<b>Success rate:</b> <code>{round((success/len(users))*100, 2)}%</code>",
                chat_id=message.chat.id,
                message_id=progress_msg.message_id
            )

        log_to_vps(f"Bot {bot_name} started - Sessions: {len(sessions)}")
        print(f"{bot_name} is running...")
        print(f"Available sessions: {len(sessions)}")
        print(f"Admin: {bot_admin}")
        print(f"API credentials: {len(API_CREDENTIALS)}")
        bot.polling(none_stop=True)
        
    except Exception as e:
        error_msg = f"Bot error: {e}"
        log_to_vps(error_msg)
        print(error_msg)
        time.sleep(3)
