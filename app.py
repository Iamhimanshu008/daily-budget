import streamlit as st
from database import ExpenseTrackerDB
from utils import load_css

# Import the page functions from the new 'views' directory
from views.auth import show_auth_page
from views.dashboard import show_dashboard
from views.add_expense import show_add_expense
from views.manage_expenses import show_manage_expenses
from views.budget import show_budget_tracker
from views.export import show_export_data

# Configure the page (must be the first Streamlit command)
st.set_page_config(
    page_title="Daily Budget",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded"
)


def main():
    """Main application function."""
    # Load external CSS
    load_css("static/style.css")

    # Initialize the database
    db = ExpenseTrackerDB()

    # Initialize session state
    if 'user' not in st.session_state:
        st.session_state.user = None

    # Main application header
    st.markdown('''
    <div class="main-header">
        <h1><i class="fas fa-chart-line icon-large"></i>Daily Budget</h1>
        <p>Professional expense management with advanced analytics and insights</p>
    </div>
    ''', unsafe_allow_html=True)

    # Authentication Flow
    if st.session_state.user is None:
        show_auth_page(db)
    else:
        # If the user is authenticated, show the main application
        with st.sidebar:
            st.markdown(f'''
            <div style="background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 1.5rem; border-radius: 10px; margin-bottom: 1rem;">
                <h3><i class="fas fa-user-circle icon"></i>Welcome, {st.session_state.user['username']}!</h3>
                <p style="margin: 0; opacity: 0.9;">Ready to track your expenses?</p>
            </div>
            ''', unsafe_allow_html=True)

            page_options = [
                "Dashboard", "Add Expense", "Manage Expenses",
                "Budget Tracker", "Export Data"
            ]

            page_icons = {
                "Dashboard": "📊", "Add Expense": "➕", "Manage Expenses": "✏️",
                "Budget Tracker": "🎯", "Export Data": "📥"
            }

            # This is our custom navigator, which we want to keep
            page = st.selectbox(
                "Navigate",
                options=page_options,
                format_func=lambda x: f"{page_icons.get(x, '')} {x}"
            )

            st.markdown("---")

            # Quick stats in the sidebar
            expenses_df = db.get_expenses(st.session_state.user['id'])
            if not expenses_df.empty:
                total_spent = expenses_df['amount'].sum()
                total_expenses = len(expenses_df)
                st.markdown(f'''
                <div style="background: #f8fafc; padding: 1rem; border-radius: 8px; margin: 1rem 0;">
                    <h4 style="margin: 0 0 0.5rem 0; color: #1f2937;">Quick Stats</h4>
                    <p style="margin: 0.25rem 0;"><i class="fas fa-dollar-sign"></i> Total Spent: <strong>₹{total_spent:,.2f}</strong></p>
                    <p style="margin: 0.25rem 0;"><i class="fas fa-list"></i> Total Records: <strong>{total_expenses}</strong></p>
                </div>
                ''', unsafe_allow_html=True)

            st.markdown("---")

            if st.button("🚪 Logout", use_container_width=True, type="secondary"):
                st.session_state.user = None
                st.rerun()

        # Main content routing based on sidebar selection
        page_map = {
            "Dashboard": show_dashboard,
            "Add Expense": show_add_expense,
            "Manage Expenses": show_manage_expenses,
            "Budget Tracker": show_budget_tracker,
            "Export Data": show_export_data
        }

        # Call the selected page's function
        page_function = page_map.get(page)
        if page_function:
            page_function(db)


if __name__ == "__main__":
    main()
