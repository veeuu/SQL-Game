# Multi-Round Duo Mode Logic

def calculate_round_winner(room_id, round_number, db_conn):
    """Determine winner of a specific round based on submissions."""
    c = db_conn.cursor()
    
    c.execute("""
        SELECT user_id, execution_time, submitted_at 
        FROM duo_submissions 
        WHERE room_id = ? AND round_number = ? AND is_correct = 1
        ORDER BY submitted_at ASC
    """, (room_id, round_number))
    
    submissions = c.fetchall()
    
    if len(submissions) == 0:
        return None, None, None
    
    winner_id = submissions[0][0]
    winner_time = submissions[0][1]
    loser_time = submissions[1][1] if len(submissions) > 1 else None
    
    return winner_id, winner_time, loser_time

def update_room_scores(room_id, round_winner_id, db_conn):
    """Update player scores in the room after a round."""
    c = db_conn.cursor()
    
    c.execute("SELECT creator_id, opponent_id, player1_score, player2_score FROM rooms WHERE id = ?", 
              (room_id,))
    room = c.fetchone()
    
    if not room:
        return False
    
    creator_id, opponent_id, p1_score, p2_score = room
    
    if round_winner_id == creator_id:
        p1_score += 1
    elif round_winner_id == opponent_id:
        p2_score += 1
    
    c.execute("""
        UPDATE rooms 
        SET player1_score = ?, player2_score = ?
        WHERE id = ?
    """, (p1_score, p2_score, room_id))
    
    db_conn.commit()
    return True

def check_match_winner(room_id, db_conn):
    """Check if someone has won the overall match."""
    c = db_conn.cursor()
    
    c.execute("""
        SELECT creator_id, opponent_id, player1_score, player2_score, 
               total_rounds, current_round
        FROM rooms WHERE id = ?
    """, (room_id,))
    
    room = c.fetchone()
    if not room:
        return None, None
    
    creator_id, opponent_id, p1_score, p2_score, total_rounds, current_round = room
    
    rounds_to_win = (total_rounds // 2) + 1
    
    if p1_score >= rounds_to_win:
        return creator_id, f"{p1_score}-{p2_score}"
    elif p2_score >= rounds_to_win:
        return opponent_id, f"{p2_score}-{p1_score}"
    
    if current_round > total_rounds:
        if p1_score > p2_score:
            return creator_id, f"{p1_score}-{p2_score}"
        elif p2_score > p1_score:
            return opponent_id, f"{p2_score}-{p1_score}"
    
    return None, None

def advance_to_next_round(room_id, db_conn):
    """Move to the next round in the match."""
    c = db_conn.cursor()
    
    c.execute("""
        UPDATE rooms 
        SET current_round = current_round + 1
        WHERE id = ?
    """, (room_id,))
    
    db_conn.commit()
    return True
