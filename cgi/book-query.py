#/usr/bin/python3

import sqlite3

import cgi

import httplib

def main():
    rows = run_query()
    if rows is False:
        query_failure()
        return False
    else:
        query_success(rows)
        return True

def run_query():
    """Run the queries against the sqlite backend and return the resulting rows."""
    query = cgi.FieldStorage()
    search_by = query.getvalue("searchby")
    search_type = query.getvalue("searchtype")
    # Convert search type to sql statement chunk
    if search_type == 'exact':
        search_type = '=?'
    else:
        search_type = " like ?"
    # Prepend and append bits to search statement based on search type
    if search_type == " like ?":
        search = "%" + query.getvalue("search") + "%"
    else:
        search = query.getvalue("search")
    books_db = sqlite3.connect("books.sqlite")
    query_cursor = books_db.cursor()
    search_columns = ["title", "author", "summary",
                     "publisher", "dewey", "locc"]
    partial_sql = ("select key, title, author, pubtext, edition,"
                   " availability from books where ")
    # Handle special cases
    if search_by == 'subject':
        query_cursor.execute("select * from books;")
        results = query_cursor.fetchall()
        matching_rows = []
        for row in results:
            subjects = row[7].split(",")
            for subject in subjects:
                if search_type == " like ?":
                    if search in subject:
                        matching_rows.append(row)
                    else:
                        pass
                else:
                    if search == subject:
                        matching_rows.append(row)
                    else:
                        pass
        return matching_rows
    elif search_by == 'isbn':
        query_cursor.execute(partial_sql + "isbn10" + search_type + ";", (search,))
        intermediate_results = query_cursor.fetchall()
        query_cursor.execute(partial_sql + "isbn13" + search_type + ";", (search,))
        return intermediate_results + query_cursor.fetchall()
    elif search_by == 'availability':
        if search[0] == "%":
            search = search[1]
        else:
            pass
        if search == '0' or search == 'false' or search == 'False':
            query_cursor.execute(partial_sql + "availability=0;")
            return query_cursor.fetchall()
        elif search == '1' or search == 'true' or search == 'True':
            query_cursor.execute(partial_sql + "availability=1;")
        else:
            return False
    # Handle all other 'generic' cases.
    elif search_by in search_columns:
        partial_sql = ()
        query_cursor.execute(partial_sql + search_by + search_type + ";", (search,))
        return query_cursor.fetchall()
    else:
        return False

def query_failure():
    """Give an HTTP response indicating the query failed."""
    #HTTP Headers
    print(
    # Seperator between header and HTML
    print()