import csv
import io
from datetime import datetime
from configer import get_header

# 常数的设置
LOG_FILE = 'log.csv'  # Location of your log file
RPD = 0.2  # 1/5 1minBodywork:4minsMindwork EXPECTED_RATIO_P_D Expected Mental workout of the total Duration
header = get_header()

class Check_Fix:
    def __init__(self):
        self.log_file = LOG_FILE
        self.R = RPD

    def validate_and_correct_data(self, timestamp):
        # This function retrieves the data for the given timestamp from the log file, validates it, and corrects any errors
        data = get_row_by_timestamp(timestamp)
        # make a string, if anymistake, add info to the string.
        error_info = data.get("Log Notes", "")

        try:
            r = float(data["RatioP"])
            D = float(data["Duration"])

            # t = float(data["TotalP"])
            # TODO Check D "Duration"

            # Check n
            # "need Physical Expenditure"
            n = float(data["NeedP"])
            correct_n = self._calculate_MxP(r)
            if abs(n - correct_n) > 2:  # tolerance of 2 minute
                error_info += f' needP/{correct_n}/{n}' # error info
                data["NeedP"] = correct_n

            # Check M & P
            # "Mental Expenditure" & "Physical Expenditure"
            M = float(data["Mental Expenditure"])
            P = float(data["Physical Expenditure"])
            correct_M, correct_P = self._calculate_expenditure(D, r)
            if abs(M - correct_M) > 2:  # tolerance of 1 minute
                data["Mental Expenditure"] = correct_M
            if abs(P - correct_P) > 2:  # tolerance of 1 minute
                data["Physical Expenditure"] = correct_P
            
            # Append error info to Log Notes
            data["Log Notes"] = error_info            
            # Write the corrected data back to the csv file
            write_row_by_timestamp(timestamp, data)

        except Exception as e:
            # Add error info to Log Notes
            log_notes = data.get("Log Notes", "")
            log_notes += f' error(subject/expected/actual): {e.args[0]}'
            data["Log Notes"] = log_notes
            # Write the corrected data back to the csv file
            write_row_by_timestamp(timestamp, data)

    def _to_datetime(self, timestamp):
        return datetime.datetime.fromisoformat(timestamp)

    def _calculate_duration(self, start_time, end_time):
        # Calculate the duration between start_time and end_time in minutes
        duration = end_time - start_time
        return duration.total_seconds() / 60  # Convert duration to minutes

    def _calculate_expenditure(self, D, r):
        # Calculate the mental and physical expenditure
        M=D-D*r
        P=D*r
        return M, P

    def _calculate_MxP(self, MvP):
        # Calculate the MxP (mental-physical balance difference time)
        MxP = MvP[0] / self.R - MvP[1]
        return MxP

        
def write_row_by_timestamp(timestamp, row):
    with open(LOG_FILE, 'r') as file:
        reader = csv.DictReader(file)
        data = list(reader)
        fieldnames = reader.fieldnames

    # Check if a row with the given timestamp exists
    for i, row_data in enumerate(data):
        if row_data["Timestamp"] == timestamp:
            # Update the existing row
            data[i] = row
            break
    else:
        # Append a new row if no existing row was found
        data.append(row)

    # Write the modified data back to the CSV file
    with open(LOG_FILE, 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

def get_row_by_timestamp(timestamp):
    # This function retrieves the row with the given timestamp from the log file
    with open(LOG_FILE, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row["Timestamp"] == timestamp:
                return row

def row_to_csv_string(row):
    # This function converts a dictionary row to a CSV string
    return ','.join([str(value) for value in row.values()])

def csv_string_to_row(csv_string, fieldnames):
    # This function converts a CSV string to a dictionary row
    csv_file = io.StringIO(csv_string)
    reader = csv.DictReader(csv_file, fieldnames=fieldnames)
    return next(reader)

def time8601(time):
    return time.strftime('%Y-%m-%d %H:%M')

def insert(csv_string):
    # This function converts a CSV string to a dictionary and writes it to the CSV file
    row = csv_string_to_row(csv_string, header)
    write_row_by_timestamp(row['Timestamp'], row)
    Check_Fix().validate_and_correct_data(row['Timestamp'])
    return row_to_csv_string(get_row_by_timestamp(row['Timestamp']))

def update(csv_string):
    # use the timekey to get the row and update it without any check
    row = csv_string_to_row(csv_string, header)
    write_row_by_timestamp(row['Timestamp'], row)
    return "updated" + row_to_csv_string(get_row_by_timestamp(row['Timestamp']))

def rebuild_header():
    # Use header from header to rebuild the header of the log file
    with open(LOG_FILE, 'r') as file:
        reader = csv.reader(file)
        data = list(reader)
    with open(LOG_FILE, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(header)
        for row in data:
            writer.writerow(row)

def end(csv_string):
    row = csv_string_to_row(csv_string, header)
    write_row_by_timestamp(row['Timestamp'], row)
    # Write an empty row
    with open(LOG_FILE, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([''] * len(header))

    # create a new log data, with current time as timestamp
    # the rest for the row is empty
    # make it to csv, and return that row
def init():
    # Define the values
    values = {
        'Timestamp': time8601(datetime.now()),
        'NeedP': 3,
        'TotalP': 3,
        'Mental Expenditure': 20,
        'Physical Expenditure': 2,
        'Log Notes': "Begin there"
    }

    # Initialize the row with empty strings
    row = {fieldname: '' for fieldname in header}

    # Update the row with the defined values
    for key, value in values.items():
        if key in row:
            row[key] = str(value)
        else:
            return f"Init Key '{key}' does not exist in the row."

    write_row_by_timestamp(row['Timestamp'], row)
    return row_to_csv_string(get_row_by_timestamp(row['Timestamp']))

rebuild_header