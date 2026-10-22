# Student Complaint Management System (Streamlit)

## Kaise chalayein

1. Virtual environment banao (optional but recommended):
   ```
   python -m venv venv
   venv\Scripts\activate      # Windows
   source venv/bin/activate   # Mac/Linux
   ```

2. Requirements install karo:
   ```
   pip install -r requirements.txt
   ```

3. App run karo:
   ```
   streamlit run app.py
   ```

4. Browser automatically khul jayega: `http://localhost:8501`

## Login details

- **Admin (pehle se bana hua):** username `admin`, password `admin123`
- **Student:** "Register" tab se naya account banao

## Kaam kaise karta hai

- Database SQLite hai (`complaints.db` file automatically ban jayegi first run par) — koi extra setup nahi chahiye.
- Student login karke complaint file kar sakta hai aur apna status (Pending/In Progress/Resolved) track kar sakta hai.
- Admin saari complaints dekh sakta hai, status filter kar sakta hai, aur status update kar sakta hai.

## Aage badhane ke ideas
- `st.metric` / `st.bar_chart` se admin dashboard par complaints ka summary chart
- Complaint ke saath image upload (`st.file_uploader`)
- Email/SMS notification jab status change ho
- Password ke liye `bcrypt` jaisa stronger hashing (abhi sha256 use ho raha hai, mini project ke liye theek hai)
