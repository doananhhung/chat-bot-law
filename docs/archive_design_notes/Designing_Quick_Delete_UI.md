<style>
    /* Force white background and black text for the whole page */
    body, .vscode-body {
        background-color: #ffffff !important;
        color: #000000 !important;
    }
    /* Style code blocks to be readable on white */
    code, pre {
        background-color: #f0f0f0 !important;
        color: #222222 !important;
    }
</style>
# DESIGN DOCUMENT: QUICK DELETE UI (SIDEBAR)
**Date:** 2026-01-13
**Status:** DRAFT
**Context:** The current deletion process requires users to select a conversation, open a settings expander, and click a delete button. This is too many clicks for managing multiple chats.

---

## 1. OBJECTIVE
Improve the User Experience (UX) by placing a "Quick Delete" button (e.g., `x` or `🗑️`) directly next to each conversation title in the Sidebar history list.

## 2. CURRENT STATE
*   **Structure**: The sidebar iterates through `recent_sessions` and renders a single `st.button` (full width) for each session.
*   **Code Snippet**:
    ```python
    for s in recent_sessions:
        if st.button(label, ...): switch_session()
    ```

## 3. PROPOSED UI LAYOUT

To achieve the "Title + Delete Button" layout in Streamlit, we will use `st.columns` for each list item.

### Layout Mockup
```text
| Sidebar ------------------------|
|                                 |
| [ + New Chat ]                  |
|                                 |
| Recent:                         |
| [Chat A               ] [ X ]   |
| [Chat B (Active)      ] [ X ]   |
| [Chat C               ] [ X ]   |
|                                 |
|---------------------------------|
```

### Technical Component Strategy
*   **Grid System**: Use `col1, col2 = st.columns([0.85, 0.15])`.
*   **Column 1 (Select)**: Contains the session title button. Clicking it switches the `session_id`.
*   **Column 2 (Delete)**: Contains the delete button (icon `✖` or `🗑`). Clicking it triggers the deletion logic.

## 4. INTERACTION LOGIC

### 4.1. Selecting a Session (Column 1)
*   **Action**: User clicks the Title.
*   **Result**: 
    *   Update `st.session_state.session_id`.
    *   `st.rerun()`.

### 4.2. Deleting a Session (Column 2)
*   **Action**: User clicks `✖`.
*   **Logic**:
    1.  **Backend**: Call `repo.delete_session(target_id)`.
    2.  **State Check**:
        *   **Scenario A: User deleted the INACTIVE session.**
            *   Do not change `st.session_state.session_id`.
            *   Just `st.rerun()` to refresh the list.
        *   **Scenario B: User deleted the ACTIVE session.**
            *   The current view is now invalid.
            *   Logic: Switch to the *next available* session in the list.
            *   If the list is empty (user deleted the last one), create a new "New Chat" session automatically.
            *   Update `st.session_state.session_id`.
            *   `st.rerun()`.

## 5. DETAILED IMPLEMENTATION PLAN

### Step 1: CSS Tweaks (Optional but Recommended)
Streamlit columns can sometimes have large gaps. We might need small custom CSS to reduce the padding between the Title button and the Delete button for a cohesive look.

### Step 2: Refactor Sidebar Loop
Modify the `for s in recent_sessions:` loop in `app.py`.

**Pseudocode:**
```python
for s in recent_sessions:
    col_nav, col_del = st.columns([0.85, 0.15])
    
    with col_nav:
        # Highlight active
        type_ = "primary" if s.id == st.session_state.session_id else "secondary"
        if st.button(s.title, key=f"nav_{s.id}", type=type_):
            switch_session(s.id)
            
    with col_del:
        # Use a distinct key
        if st.button("🗑", key=f"del_{s.id}", help="Xóa hội thoại này"):
            handle_specific_delete(s.id)
```

### Step 3: Update Helper Functions
Refactor `handle_delete_session` to accept an explicit `target_id` (the one to be deleted) and compare it against `current_id` (the one currently being viewed) to decide if a switch is needed.

## 6. EDGE CASES & RISKS

*   **Accidental Deletion**: Since `st.button` is immediate, there is no "Are you sure?" confirmation. 
    *   *Mitigation*: For this MVP phase, we accept this risk for speed (as per "Quick Delete" requirement). In the future, we can use `st.popover` (if upgrading Streamlit) or a "Undo" toast.
*   **Long Titles**: Long titles might truncate awkwardly in the 85% width column. Streamlit handles this by ellipsizing, which is acceptable.
*   **Mobile View**: On very narrow screens, the [0.85, 0.15] ratio might squish the delete button. Streamlit stacks columns on mobile, which might look like "Title" then "Delete" below it.
    *   *Mitigation*: Check `st.columns` behavior. Usually, it keeps side-by-side on reasonable widths, but stacks on mobile. This is acceptable for now.
