"""
Generate mock user and usage data for the SaaS Task Management App
This script creates realistic user behavior patterns to help identify the "aha moment"
"""
import psycopg2
from datetime import datetime, timedelta
import random
import json

# Set seed for reproducibility
random.seed(42)

# Database connection parameters
DB_PARAMS = {
    'dbname': 'taskmanagement',
    'user': 'postgres',
    'password': 'postgres',
    'host': 'db',
    'port': '5432'
}

# User behavior patterns
ACTION_TYPES = [
    'login',
    'create_project',
    'create_task',
    'complete_task',
    'invite_team_member',
    'view_dashboard',
    'update_task',
    'delete_task',
    'archive_project',
    'set_task_priority',
    'add_task_comment',
    'upload_file',
    'create_task_list',
    'set_due_date'
]

def wait_for_db(max_retries=30):
    """Wait for database to be ready"""
    import time
    for i in range(max_retries):
        try:
            conn = psycopg2.connect(**DB_PARAMS)
            conn.close()
            print("Database is ready!")
            return True
        except psycopg2.OperationalError:
            print(f"Waiting for database... ({i+1}/{max_retries})")
            time.sleep(2)
    return False

def generate_users(conn, num_users=200):
    """Generate mock users"""
    cursor = conn.cursor()
    
    # Clear existing data
    cursor.execute("TRUNCATE users CASCADE;")
    
    users = []
    base_date = datetime(2024, 1, 1)
    
    for i in range(num_users):
        email = f"user{i+1}@example.com"
        username = f"user_{i+1}"
        # Users sign up over a 6-month period
        created_at = base_date + timedelta(days=random.randint(0, 180))
        
        cursor.execute(
            "INSERT INTO users (email, username, created_at) VALUES (%s, %s, %s) RETURNING user_id",
            (email, username, created_at)
        )
        user_id = cursor.fetchone()[0]
        users.append({'user_id': user_id, 'created_at': created_at})
    
    conn.commit()
    print(f"Generated {num_users} users")
    return users

def generate_user_behavior(conn, users):
    """
    Generate realistic user behavior with different engagement patterns
    Some users will be highly engaged (likely to convert), others less so
    """
    cursor = conn.cursor()
    
    for user in users:
        user_id = user['user_id']
        signup_date = user['created_at']
        
        # Determine user engagement level (this correlates with conversion)
        engagement_level = random.choices(
            ['low', 'medium', 'high'],
            weights=[0.5, 0.3, 0.2]  # Most users have low engagement
        )[0]
        
        # Generate actions based on engagement level
        if engagement_level == 'low':
            num_actions = random.randint(1, 10)
            num_projects = random.randint(0, 1)
            num_tasks = random.randint(0, 5)
            conversion_probability = 0.05
        elif engagement_level == 'medium':
            num_actions = random.randint(10, 40)
            num_projects = random.randint(1, 3)
            num_tasks = random.randint(5, 20)
            conversion_probability = 0.30
        else:  # high engagement
            num_actions = random.randint(40, 150)
            num_projects = random.randint(2, 8)
            num_tasks = random.randint(15, 60)
            conversion_probability = 0.75
        
        # Generate projects
        project_ids = []
        for p in range(num_projects):
            project_created_at = signup_date + timedelta(hours=random.randint(1, 72))
            cursor.execute(
                "INSERT INTO projects (user_id, project_name, created_at) VALUES (%s, %s, %s) RETURNING project_id",
                (user_id, f"Project {p+1}", project_created_at)
            )
            project_ids.append(cursor.fetchone()[0])
        
        # Generate tasks
        completed_tasks = 0
        for t in range(num_tasks):
            if project_ids:
                project_id = random.choice(project_ids)
                task_created_at = signup_date + timedelta(hours=random.randint(1, 168))
                status = random.choice(['pending', 'in_progress', 'completed'])
                
                completed_at = None
                if status == 'completed':
                    completed_at = task_created_at + timedelta(hours=random.randint(1, 48))
                    completed_tasks += 1
                
                cursor.execute(
                    """INSERT INTO tasks (project_id, user_id, title, status, priority, created_at, completed_at) 
                       VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                    (project_id, user_id, f"Task {t+1}", status, 
                     random.choice(['low', 'medium', 'high']), task_created_at, completed_at)
                )
        
        # Generate user actions (event tracking)
        action_timestamp = signup_date
        
        # First action is always login
        cursor.execute(
            "INSERT INTO user_actions (user_id, action_type, created_at) VALUES (%s, %s, %s)",
            (user_id, 'login', action_timestamp)
        )
        
        # Generate other actions
        for _ in range(num_actions - 1):
            action_timestamp = action_timestamp + timedelta(minutes=random.randint(1, 720))
            action_type = random.choice(ACTION_TYPES)
            
            action_details = {}
            if action_type == 'create_project':
                action_details = {'project_count': len(project_ids)}
            elif action_type == 'create_task':
                action_details = {'task_count': num_tasks}
            elif action_type == 'complete_task':
                action_details = {'completed_count': completed_tasks}
            elif action_type == 'invite_team_member':
                action_details = {'invited': True}
            
            cursor.execute(
                "INSERT INTO user_actions (user_id, action_type, action_details, created_at) VALUES (%s, %s, %s, %s)",
                (user_id, action_type, json.dumps(action_details), action_timestamp)
            )
        
        # Determine if user converts to paid plan
        if random.random() < conversion_probability:
            # User converts, typically after 3-14 days
            conversion_date = signup_date + timedelta(days=random.randint(3, 14))
            plan_id = random.choice([2, 3])  # Pro or Business plan
            
            cursor.execute(
                "INSERT INTO user_subscriptions (user_id, plan_id, subscribed_at) VALUES (%s, %s, %s)",
                (user_id, plan_id, conversion_date)
            )
    
    conn.commit()
    print(f"Generated user behavior patterns and {cursor.rowcount} actions")

def generate_team_interactions(conn):
    """Generate team member interactions for collaborative users"""
    cursor = conn.cursor()
    
    # Get users with subscriptions (they can add team members)
    cursor.execute("""
        SELECT u.user_id, p.project_id 
        FROM users u
        JOIN user_subscriptions us ON u.user_id = us.user_id
        JOIN projects p ON u.user_id = p.user_id
        WHERE us.is_active = true
    """)
    
    eligible_combos = cursor.fetchall()
    
    # Add some team members
    for user_id, project_id in eligible_combos:
        if random.random() < 0.4:  # 40% chance of adding team member
            # Get a random user to add as team member
            cursor.execute("SELECT user_id FROM users WHERE user_id != %s ORDER BY RANDOM() LIMIT 1", (user_id,))
            result = cursor.fetchone()
            if result:
                member_id = result[0]
                cursor.execute(
                    "INSERT INTO team_members (project_id, user_id, role) VALUES (%s, %s, %s)",
                    (project_id, member_id, 'member')
                )
    
    conn.commit()
    print("Generated team member interactions")

def main():
    print("Starting data generation...")
    
    # Wait for database
    if not wait_for_db():
        print("Could not connect to database")
        return
    
    # Connect to database
    conn = psycopg2.connect(**DB_PARAMS)
    
    try:
        # Generate data
        users = generate_users(conn, num_users=200)
        generate_user_behavior(conn, users)
        generate_team_interactions(conn)
        
        print("\n✓ Data generation complete!")
        
        # Print summary statistics
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM users")
        print(f"\nTotal users: {cursor.fetchone()[0]}")
        
        cursor.execute("SELECT COUNT(*) FROM user_subscriptions WHERE is_active = true")
        print(f"Converted users: {cursor.fetchone()[0]}")
        
        cursor.execute("SELECT COUNT(*) FROM projects")
        print(f"Total projects: {cursor.fetchone()[0]}")
        
        cursor.execute("SELECT COUNT(*) FROM tasks")
        print(f"Total tasks: {cursor.fetchone()[0]}")
        
        cursor.execute("SELECT COUNT(*) FROM user_actions")
        print(f"Total user actions: {cursor.fetchone()[0]}")
        
    finally:
        conn.close()

if __name__ == '__main__':
    main()
