"""
Generate a visual diagram of the database schema
"""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import os

def create_schema_diagram():
    fig, ax = plt.subplots(1, 1, figsize=(16, 12))
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 12)
    ax.axis('off')
    
    # Define colors
    table_color = '#E8F4F8'
    pk_color = '#FFE5B4'
    fk_color = '#FFB6C1'
    
    # Table definitions: (x, y, width, height, name, fields)
    tables = [
        {
            'x': 0.5, 'y': 8, 'width': 3, 'height': 2.5, 'name': 'users',
            'fields': [
                ('user_id', 'PK'),
                ('email', ''),
                ('username', ''),
                ('created_at', ''),
                ('is_active', '')
            ]
        },
        {
            'x': 4.5, 'y': 8, 'width': 3, 'height': 2, 'name': 'subscription_plans',
            'fields': [
                ('plan_id', 'PK'),
                ('plan_name', ''),
                ('price', ''),
                ('features', '')
            ]
        },
        {
            'x': 8.5, 'y': 8, 'width': 3.5, 'height': 2.5, 'name': 'user_subscriptions',
            'fields': [
                ('subscription_id', 'PK'),
                ('user_id', 'FK'),
                ('plan_id', 'FK'),
                ('subscribed_at', ''),
                ('is_active', '')
            ]
        },
        {
            'x': 0.5, 'y': 4.5, 'width': 3, 'height': 2.5, 'name': 'projects',
            'fields': [
                ('project_id', 'PK'),
                ('user_id', 'FK'),
                ('project_name', ''),
                ('description', ''),
                ('created_at', '')
            ]
        },
        {
            'x': 4.5, 'y': 4.5, 'width': 3, 'height': 3, 'name': 'tasks',
            'fields': [
                ('task_id', 'PK'),
                ('project_id', 'FK'),
                ('user_id', 'FK'),
                ('title', ''),
                ('status', ''),
                ('priority', ''),
                ('created_at', ''),
                ('completed_at', '')
            ]
        },
        {
            'x': 8.5, 'y': 4.5, 'width': 3.5, 'height': 2.5, 'name': 'user_actions',
            'fields': [
                ('action_id', 'PK'),
                ('user_id', 'FK'),
                ('action_type', ''),
                ('action_details', ''),
                ('created_at', '')
            ]
        },
        {
            'x': 0.5, 'y': 1, 'width': 3, 'height': 2.5, 'name': 'team_members',
            'fields': [
                ('team_member_id', 'PK'),
                ('project_id', 'FK'),
                ('user_id', 'FK'),
                ('role', ''),
                ('added_at', '')
            ]
        }
    ]
    
    # Draw tables
    for table in tables:
        # Draw table box
        box = FancyBboxPatch(
            (table['x'], table['y']),
            table['width'], table['height'],
            boxstyle="round,pad=0.05",
            edgecolor='#333',
            facecolor=table_color,
            linewidth=2
        )
        ax.add_patch(box)
        
        # Draw table name
        ax.text(
            table['x'] + table['width']/2,
            table['y'] + table['height'] - 0.2,
            table['name'],
            fontsize=12,
            fontweight='bold',
            ha='center',
            va='top'
        )
        
        # Draw fields
        field_y = table['y'] + table['height'] - 0.5
        for field, field_type in table['fields']:
            color = pk_color if field_type == 'PK' else (fk_color if field_type == 'FK' else 'white')
            field_box = mpatches.Rectangle(
                (table['x'] + 0.1, field_y - 0.25),
                table['width'] - 0.2, 0.22,
                facecolor=color,
                edgecolor='#666',
                linewidth=0.5
            )
            ax.add_patch(field_box)
            
            field_text = f"{field}" + (f" ({field_type})" if field_type else "")
            ax.text(
                table['x'] + 0.15,
                field_y - 0.14,
                field_text,
                fontsize=8,
                va='center'
            )
            field_y -= 0.28
    
    # Define relationships (arrows)
    relationships = [
        # From user_subscriptions to users
        {'from': (8.5, 9.25), 'to': (3.5, 9.25), 'label': ''},
        # From user_subscriptions to subscription_plans
        {'from': (8.5, 8.75), 'to': (7.5, 9), 'label': ''},
        # From projects to users
        {'from': (2, 7), 'to': (2, 8), 'label': ''},
        # From tasks to projects
        {'from': (4.5, 6), 'to': (3.5, 6), 'label': ''},
        # From tasks to users
        {'from': (6, 7.5), 'to': (3, 8.5), 'label': ''},
        # From user_actions to users
        {'from': (10.25, 7), 'to': (2.5, 8), 'label': ''},
        # From team_members to projects
        {'from': (2, 3.5), 'to': (2, 4.5), 'label': ''},
        # From team_members to users
        {'from': (3.5, 2.5), 'to': (3.5, 8), 'label': ''},
    ]
    
    # Draw relationships
    for rel in relationships:
        arrow = FancyArrowPatch(
            rel['from'], rel['to'],
            arrowstyle='-|>',
            color='#666',
            linewidth=1.5,
            mutation_scale=15,
            linestyle='--'
        )
        ax.add_patch(arrow)
    
    # Add title and legend
    ax.text(8, 11.5, 'SaaS Task Management Database Schema', 
            fontsize=18, fontweight='bold', ha='center')
    
    # Create legend
    legend_elements = [
        mpatches.Patch(facecolor=pk_color, edgecolor='#666', label='Primary Key'),
        mpatches.Patch(facecolor=fk_color, edgecolor='#666', label='Foreign Key'),
        mpatches.Patch(facecolor='white', edgecolor='#666', label='Regular Field'),
    ]
    ax.legend(handles=legend_elements, loc='upper right', fontsize=10)
    
    # Add note about user_actions
    note_text = "Note: user_actions table tracks all user behavior\nCritical for finding the 'aha moment'"
    ax.text(12.5, 3, note_text, fontsize=9, 
            bbox=dict(boxstyle='round', facecolor='#FFFFCC', alpha=0.8),
            verticalalignment='top')
    
    plt.tight_layout()
    
    # Save diagram
    output_path = '/output/schema_diagram.png'
    os.makedirs('/output', exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"Schema diagram saved to {output_path}")
    plt.close()

if __name__ == '__main__':
    create_schema_diagram()
