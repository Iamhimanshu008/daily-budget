# pages/manage_expenses.py
import streamlit as st
import pandas as pd
from database import ExpenseTrackerDB


def show_manage_expenses(db: ExpenseTrackerDB):
    """Display expense management interface with enhanced filtering"""
    st.markdown('<h2><i class="fas fa-edit icon"></i>Manage Your Expenses</h2>',
                unsafe_allow_html=True)

    expenses_df = db.get_expenses(st.session_state.user['id'])

    if expenses_df.empty:
        st.markdown('''
        <div style="text-align: center; padding: 3rem; background: #f8fafc; border-radius: 15px;">
            <i class="fas fa-inbox" style="font-size: 4rem; color: #9ca3af; margin-bottom: 1rem;"></i>
            <h3 style="color: #6b7280;">No Expenses to Manage</h3>
            <p style="color: #9ca3af;">Start by adding some expenses to manage them here.</p>
        </div>
        ''', unsafe_allow_html=True)
        return

    # Enhanced filtering section
    st.markdown('<h4><i class="fas fa-filter icon"></i>Filter & Search</h4>',
                unsafe_allow_html=True)

    filter_col1, filter_col2, filter_col3, filter_col4 = st.columns(4)

    with filter_col1:
        categories = ['All Categories'] + \
            sorted(expenses_df['category'].unique().tolist())
        selected_category = st.selectbox("📂 Category", categories)

    with filter_col2:
        min_date = expenses_df['date'].min()
        max_date = expenses_df['date'].max()
        date_range = st.date_input(
            "📅 Date Range",
            value=(pd.to_datetime(min_date).date(),
                   pd.to_datetime(max_date).date()),
            key="manage_date_filter"
        )

    with filter_col3:
        min_amount = float(expenses_df['amount'].min())
        max_amount = float(expenses_df['amount'].max())
        amount_range = st.slider(
            "💰 Amount Range",
            min_value=min_amount,
            max_value=max_amount,
            value=(min_amount, max_amount),
            step=0.01
        )

    with filter_col4:
        search_term = st.text_input(
            "🔍 Search",
            placeholder="Search descriptions..."
        )

    # Apply filters
    filtered_df = expenses_df.copy()
    filtered_df['date'] = pd.to_datetime(filtered_df['date'])

    if selected_category != 'All Categories':
        filtered_df = filtered_df[filtered_df['category'] == selected_category]

    if len(date_range) == 2:
        start_date, end_date = date_range
        filtered_df = filtered_df[
            (filtered_df['date'].dt.date >= start_date) &
            (filtered_df['date'].dt.date <= end_date)
        ]

    filtered_df = filtered_df[
        (filtered_df['amount'] >= amount_range[0]) &
        (filtered_df['amount'] <= amount_range[1])
    ]

    if search_term:
        filtered_df = filtered_df[
            filtered_df['description'].str.contains(
                search_term, case=False, na=False
            )
        ]

    # Results summary
    total_filtered = len(filtered_df)
    total_amount = filtered_df['amount'].sum()

    st.markdown(f'''
    <div class="metric-card">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <h4><i class="fas fa-list icon"></i>Filtered Results</h4>
                <p style="margin: 0;">Showing <strong>{total_filtered}</strong> expenses totaling <strong>₹{total_amount:,.2f}</strong></p>
            </div>
            <div style="text-align: right;">
                <button onclick="window.print()" style="background: #667eea; color: white; border: none; padding: 0.5rem 1rem; border-radius: 5px; cursor: pointer;">
                    <i class="fas fa-print"></i> Print
                </button>
            </div>
        </div>
    </div>
    ''', unsafe_allow_html=True)

    st.markdown("---")

    # Expense list with enhanced UI
    if filtered_df.empty:
        st.info("No expenses match your filter criteria.")
        return

    # Sort options
    sort_col1, sort_col2 = st.columns([1, 3])
    with sort_col1:
        sort_options = ["Date (Newest)", "Date (Oldest)",
                        "Amount (High to Low)", "Amount (Low to High)", "Category A-Z"]
        sort_selection = st.selectbox("🔄 Sort by", sort_options)

    # Apply sorting
    if sort_selection == "Date (Newest)":
        filtered_df = filtered_df.sort_values('date', ascending=False)
    elif sort_selection == "Date (Oldest)":
        filtered_df = filtered_df.sort_values('date', ascending=True)
    elif sort_selection == "Amount (High to Low)":
        filtered_df = filtered_df.sort_values('amount', ascending=False)
    elif sort_selection == "Amount (Low to High)":
        filtered_df = filtered_df.sort_values('amount', ascending=True)
    elif sort_selection == "Category A-Z":
        filtered_df = filtered_df.sort_values('category', ascending=True)

    # Display expenses with edit/delete functionality
    for idx, (_, expense) in enumerate(filtered_df.iterrows()):
        with st.expander(
            f"₹{expense['amount']:.2f} • {expense['category']} • {expense['date'].strftime('%b %d, %Y')}",
            expanded=False
        ):
            expense_col1, expense_col2 = st.columns([3, 1])

            with expense_col1:
                st.markdown(f'''
                <div style="background: #f9fafb; padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
                    <p style="margin: 0.25rem 0;"><strong>💰 Amount:</strong> ₹{expense['amount']:.2f}</p>
                    <p style="margin: 0.25rem 0;"><strong>📂 Category:</strong> {expense['category']}</p>
                    <p style="margin: 0.25rem 0;"><strong>📅 Date:</strong> {expense['date'].strftime('%B %d, %Y')}</p>
                    <p style="margin: 0.25rem 0;"><strong>📝 Description:</strong> {expense['description'] if expense['description'] else 'No description'}</p>
                </div>
                ''', unsafe_allow_html=True)

            with expense_col2:
                action_col1, action_col2 = st.columns(2)

                with action_col1:
                    if st.button("✏️ Edit", key=f"edit_{expense['id']}", use_container_width=True):
                        st.session_state[f"editing_{expense['id']}"] = True
                        st.rerun()

                with action_col2:
                    if st.button("🗑️ Delete", key=f"delete_{expense['id']}", use_container_width=True, type="secondary"):
                        if st.session_state.get(f"confirm_delete_{expense['id']}", False):
                            if db.delete_expense(expense['id'], st.session_state.user['id']):
                                st.success("Expense deleted successfully!")
                                st.rerun()
                        else:
                            st.session_state[f"confirm_delete_{expense['id']}"] = True
                            st.rerun()

            # Confirmation for delete
            if st.session_state.get(f"confirm_delete_{expense['id']}", False):
                st.markdown(
                    '<div class="alert-warning"><i class="fas fa-exclamation-triangle icon"></i>Are you sure you want to delete this expense?</div>', unsafe_allow_html=True)

                confirm_col1, confirm_col2 = st.columns(2)
                with confirm_col1:
                    if st.button("Yes, Delete", key=f"confirm_yes_{expense['id']}", type="primary"):
                        if db.delete_expense(expense['id'], st.session_state.user['id']):
                            st.session_state[f"confirm_delete_{expense['id']}"] = False
                            st.success("Expense deleted!")
                            st.rerun()

                with confirm_col2:
                    if st.button("Cancel", key=f"confirm_no_{expense['id']}"):
                        st.session_state[f"confirm_delete_{expense['id']}"] = False
                        st.rerun()

            # Edit form
            if st.session_state.get(f"editing_{expense['id']}", False):
                st.markdown("---")
                st.markdown(
                    '<h5><i class="fas fa-edit icon"></i>Edit Expense</h5>', unsafe_allow_html=True)

                with st.form(f"edit_form_{expense['id']}"):
                    edit_col1, edit_col2 = st.columns(2)

                    with edit_col1:
                        new_amount = st.number_input(
                            "Amount (₹)",
                            value=float(expense['amount']),
                            min_value=0.01,
                            step=0.01
                        )

                        categories = [
                            "Food & Dining", "Transportation", "Housing", "Shopping",
                            "Healthcare", "Entertainment", "Education", "Business",
                            "Travel", "Utilities", "Clothing", "Gifts", "Other"
                        ]

                        current_category_index = categories.index(
                            expense['category']) if expense['category'] in categories else 0
                        new_category = st.selectbox(
                            "Category",
                            categories,
                            index=current_category_index
                        )

                    with edit_col2:
                        new_date = st.date_input(
                            "Date",
                            value=expense['date'].date()
                        )

                        new_description = st.text_area(
                            "Description",
                            value=expense['description'] if expense['description'] else "",
                            max_chars=200
                        )

                    # Form actions
                    form_col1, form_col2 = st.columns(2)

                    with form_col1:
                        if st.form_submit_button("💾 Save Changes", type="primary", use_container_width=True):
                            if db.update_expense(
                                expense['id'],
                                st.session_state.user['id'],
                                new_amount,
                                new_category,
                                new_description.strip(),
                                new_date.strftime('%Y-%m-%d')
                            ):
                                st.session_state[f"editing_{expense['id']}"] = False
                                st.success("Expense updated successfully!")
                                st.rerun()
                            else:
                                st.error("Failed to update expense.")

                    with form_col2:
                        if st.form_submit_button("❌ Cancel", use_container_width=True):
                            st.session_state[f"editing_{expense['id']}"] = False
                            st.rerun()
