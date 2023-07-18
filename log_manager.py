import csv
from datetime import datetime
from configer import get_header

# 常数的设置
LOG_FILE = 'log.csv'  # Location of your log file
EXPECTED_MENTAL_TO_PHYSICAL_RATIO = 4 / 1  # Expected Mental : Physical work

# 放弃time模块, 仅用`timestamp = datetime.now().replace(second=0, microsecond=0)`就够了

class Check_Fix:
    def __init__(self):
        self.log_file = LOG_FILE
        self.expected_ratio = EXPECTED_MENTAL_TO_PHYSICAL_RATIO

    def validate_and_correct_data(self, timestamp):
        # This function retrieves the data for the given timestamp from the log file, validates it, and corrects any errors
        data = get_row_by_timestamp(timestamp)

        try:
            # Check if the timestamps can be converted to datetime objects
            start_time = self._to_datetime(data["Start Time"])
            end_time = self._to_datetime(data["End Time"])

            # Check if the duration is a valid number
            duration = float(data["Duration"])
            correct_duration = self._calculate_duration(start_time, end_time)
            if abs(duration - correct_duration) > 1:  # tolerance of 1 minute
                data["Duration"] = correct_duration

            # Check if MvP is a valid ratio
            MvP = [float(x) for x in data["MvP"].split(':')]
            if len(MvP) != 2:
                raise ValueError('MvP should be a ratio of two numbers')

            # Check if MxP is a valid number
            MxP = float(data["MxP"])
            correct_MxP = self._calculate_MxP(MvP)
            if abs(MxP - correct_MxP) > 1:  # tolerance of 1 minute
                data["MxP"] = correct_MxP

            # Check if MP is a valid number
            MP = float(data["MP"])
            # Note: we don't correct MP as it depends on the previous value

            # Check if mental and physical expenditure are valid numbers
            mental_expenditure = float(data["Mental Expenditure"])
            physical_expenditure = float(data["Physical Expenditure"])
            correct_mental_expenditure, correct_physical_expenditure = self._calculate_expenditure(duration, MvP)
            if abs(mental_expenditure - correct_mental_expenditure) > 1:  # tolerance of 1 minute
                data["Mental Expenditure"] = correct_mental_expenditure
            if abs(physical_expenditure - correct_physical_expenditure) > 1:  # tolerance of 1 minute
                data["Physical Expenditure"] = correct_physical_expenditure

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

    def _calculate_expenditure(self, duration, ratio):
        # Calculate the mental and physical expenditure
        mental_expenditure = duration * ratio[0] / sum(ratio)
        physical_expenditure = duration * ratio[1] / sum(ratio)
        return mental_expenditure, physical_expenditure

    def _calculate_MxP(self, ratio):
        # Calculate the MxP (mental-physical balance difference time)
        difference = ratio[0] - ratio[1] * self.expected_ratio
        if difference < 0:
            return difference / self.expected_ratio
        else:
            return difference

        
def write_row_by_timestamp(timestamp, row):
    with open(LOG_FILE, 'r') as file:
        reader = csv.DictReader(file)
        data = list(reader)

    # Check if a row with the given timestamp exists
    for i, row_data in enumerate(data):
        if row_data["Timestamp"] == timestamp:
            # Update the existing row
            data[i] = {k: v for k, v in zip(reader.fieldnames, row)}
            break
    else:
        # Append a new row if no existing row was found
        num_columns = len(reader.fieldnames)
        row += [''] * (num_columns - len(row))
        data.append({k: v for k, v in zip(reader.fieldnames, row)})

    # Write the modified data back to the CSV file
    with open(LOG_FILE, 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=reader.fieldnames)
        writer.writeheader()
        writer.writerows(data)

    return ','.join(row)


def get_row_by_timestamp(timestamp):
        # This function retrieves the row with the given timestamp from the log file
        with open(LOG_FILE, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row["Timestamp"] == timestamp:
                    return row

def time8601(time):
    return time.strftime('%Y-%m-%d %H:%M')

def insert(date):
    # This function inserts a new row into the log file
    # assume the data input at great format but without header, it should be easily to be insert
    data = [date]
    with open(LOG_FILE, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(data)
    # get timekey from date's timestamp
    timekey = time8601(date[0])
    # then use Check_Fix.validate_and_correct_data
    # and return the row direct from the log file
    Check_Fix().validate_and_correct_data(timekey)
    return Check_Fix().get_row_by_timestamp(timekey)

def update(date):
    date = [date]
    # use the timekey to get the row and update it without any check
    write_row_by_timestamp(date[0], date)

def rebuild_header():
    # Use header from get_header() to rebuild the header of the log file
    with open(LOG_FILE, 'r') as file:
        reader = csv.reader(file)
        data = list(reader)
    with open(LOG_FILE, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(get_header())
        for row in data:
            writer.writerow(row)

def end(date):
    insert(date)
    # write an empty row to the log file
    with open(LOG_FILE, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([])

def init():
    # create a new log data, with current time as timestamp
    # the rest for the row is empty
    # make it to csv, and return that row
    date = time8601(datetime.now())
    date = [date]
    write_row_by_timestamp(date[0], date)
    row_dict = get_row_by_timestamp(date[0])
    return ','.join(row_dict.values())