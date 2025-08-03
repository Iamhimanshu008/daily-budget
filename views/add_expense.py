# pages/add_expense.py
import streamlit as st
from datetime import datetime
from database import ExpenseTrackerDB


def show_add_expense(db: ExpenseTrackerDB):
    """Display add expense form with enhanced UI"""
    st.markdown('<h2><i class="fas fa-plus-circle icon"></i>Add New Expense</h2>',
                unsafe_allow_html=True)

    # Enhanced categories with icons and descriptions
    categories = [
        ("Food & Dining", "fas fa-utensils", "Restaurants, groceries, beverages"),
        ("Transportation", "fas fa-car", "Gas, public transport, parking"),
        ("Housing", "fas fa-home", "Rent, utilities, maintenance"),
        ("Shopping", "fas fa-shopping-bag",
         "Clothing, electronics, general purchases"),
        ("Healthcare", "fas fa-heartbeat", "Medical bills, pharmacy, insurance"),
        ("Entertainment", "fas fa-film", "Movies, games, subscriptions"),
        ("Education", "fas fa-graduation-cap", "Books, courses, tuition"),
        ("Business", "fas fa-briefcase", "Office supplies, professional services"),
        ("Travel", "fas fa-plane", "Flights, hotels, vacation expenses"),
        ("Utilities", "fas fa-bolt", "Electricity, water, internet, phone"),
        ("Clothing", "fas fa-tshirt", "Apparel, shoes, accessories"),
        ("Gifts", "fas fa-gift", "Presents, donations, charity"),
        ("Other", "fas fa-ellipsis-h", "Miscellaneous expenses")
    ]

    with st.form("add_expense_form", clear_on_submit=True):
        st.markdown(
            '<h4><i class="fas fa-edit icon"></i>Expense Details</h4>', unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            amount = st.number_input(
                "💰 Amount (₹)",
                min_value=1.00,
                step=1.00,
                format="%.2f",
                help="Enter the expense amount in Rupees"
            )

            # Category selection with enhanced display
            category_names = [cat[0] for cat in categories]
            selected_category = st.selectbox(
                "📂 Category",
                options=category_names,
                help="Select the most appropriate category for this expense"
            )

        with col2:
            expense_date = st.date_input(
                "📅 Date",
                value=datetime.now().date(),
                help="Date when the expense occurred"
            )

            description = st.text_area(
                "📝 Description",
                placeholder="Enter a brief description of the expense...",
                help="Optional: Add details about this expense",
                max_chars=200
            )

        # Submit section
        st.markdown("---")

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            submit_button = st.form_submit_button(
                "💾 Add Expense",
                use_container_width=True,
                type="primary"
            )

        if submit_button:
            if amount > 0:
                if db.add_expense(
                    st.session_state.user['id'],
                    amount,
                    selected_category,
                    description.strip(),
                    expense_date.strftime('%Y-%m-%d')
                ):
                    st.markdown(
                        '<div class="alert-success"><i class="fas fa-check-circle icon"></i>Expense added successfully!</div>', unsafe_allow_html=True)
                    st.balloons()

                    # Show summary of added expense
                    st.markdown(f'''
                    <div class="metric-card" style="margin-top: 1rem;">
                        <h4><i class="fas fa-receipt icon"></i>Expense Summary</h4>
                        <p><strong>Amount:</strong> ₹{amount:.2f}</p>
                        <p><strong>Category:</strong> {selected_category}</p>
                        <p><strong>Date:</strong> {expense_date.strftime('%B %d, %Y')}</p>
                        <p><strong>Description:</strong> {description if description.strip() else 'No description provided'}</p>
                    </div>
                    ''', unsafe_allow_html=True)
                else:
                    st.markdown(
                        '<div class="alert-error"><i class="fas fa-exclamation-triangle icon"></i>Failed to add expense. Please try again.</div>', unsafe_allow_html=True)
            else:
                st.markdown(
                    '<div class="alert-warning"><i class="fas fa-info-circle icon"></i>Please enter a valid amount greater than ₹0.00.</div>', unsafe_allow_html=True)

    # Quick add buttons for common expenses
    st.markdown("---")
    st.markdown('<h4><i class="fas fa-bolt icon"></i>Quick Add</h4>',
                unsafe_allow_html=True)

    quick_expenses = [
        ("Coffee", 50, "Food & Dining"),
        ("Lunch", 120, "Food & Dining"),
        ("Gas", 350, "Transportation"),
        ("Groceries", 1000, "Food & Dining")
    ]

    cols = st.columns(len(quick_expenses))
    for i, (name, amount, category) in enumerate(quick_expenses):
        with cols[i]:
            if st.button(f"{name}\n₹{amount}", key=f"quick_{i}", use_container_width=True):
                if db.add_expense(
                    st.session_state.user['id'],
                    amount,
                    category,
                    f"Quick add: {name}",
                    datetime.now().strftime('%Y-%m-%d')
                ):
                    st.success(f"Added {name} (₹{amount}) successfully!")
                    st.rerun()
