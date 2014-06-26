# -*- coding: utf-8 -*-

from app.bdp import app
import csvvalidator as cv
import datetime, time
import re
import json
import base64
import unicodecsv as csv
import os.path
import tempfile

# Create a path to the csv data file with all the currencies
# The file is placed in the 'data' directory
currency_file = os.path.join(app.config['DATA'], 'currencies.csv')

# Extract a list of currencies from the currency data file into tuples
# Skip the first tuple since that's the header row
currencies = [(code, name) for (code,name) in
              csv.reader(open(currency_file, 'r'))][1:]

class BudgetCSV(object):
    """
    Budget data is stored in CSV files. This class wraps a CSV file to limit
    access to the file by providing headers and validators.
    """

    def __init__(self, csvfile, *args, **kwargs):
        self.csvfile = csvfile
        self.headers = self._get_headers()

    @property
    def file(self):
        # Reset file and return the handle
        self.csvfile.seek(0)
        return self.csvfile

    def _get_headers(self):
        """
        Get CSV file headers
        """

        # Headers are alway the first row of a CSV file
        reader = csv.reader(self.file)
        return reader.next()

    def get_header_index(self, header):
        """
        Gets the index of the input header in the CSV's headers.
        """
        try:
            i = self._get_headers().index(header)
        except:
            i = -1
        return i

    def append_columns(self, column_names, row_function):
        """
        Adds new columns to the CSV.

        Takes a list of names of the new columns (column_name) and a
        function to apply to each row to yield up the values of those
        columns for the row. (Columns with a constant value can simply
        use functions that return a constant value.)

        Internally, this method works with DictReader and DictWriter
        objects. The return value of row_function ought to be a dictionary
        that can be merged with the rows from the CSV as rendered
        by DictReader.

        Note that this *directly modifies* the wrapped CSV
        file, so it's not a good idea to use this unless
        you've already created a defensive copy.
        """

        # Store the old field names.
        old_fields = self._get_headers()

        # Set up the new field names.
        new_fields = old_fields + column_names
        header_row = {}
        for field in new_fields:
            header_row[field] = field

        # Create a new temp file, where the changes
        # will be written before the main file is overwritten.
        tmp = tempfile.TemporaryFile()
        tmp_writer = csv.DictWriter(tmp, fieldnames=new_fields)

        # Open a reader with the CSV's file.
        reader = csv.DictReader(self.file)

        tmp_writer.writerow(header_row)
        # For each row in the CSV, write the row plus the
        # new value computed with row_function.
        for row in reader:
            row.update(row_function(row))
            tmp_writer.writerow(row)

        # Rewind the temp file.
        tmp.seek(0)

        # Create a new CSV reader and writer.
        temp_reader = csv.reader(tmp)
        file_name = self.file.name
        new_file = open(file_name,"r+")
        writer = csv.writer(new_file)
        # Rewind the file and overwrite it.
        new_file.seek(0)
        new_file.truncate()
        for row in temp_reader:
            writer.writerow(row)
        new_file.close()

        # Close the temp file. It'll delete automatically.
        tmp.close()
        # Create a new file session for the CSV object.
        self.csvfile = open(file_name,"r")

    def validate(self, type, deep=True):
        """
        Validates the CSV on the basis of supplied type information.
        """

        field_requirements = {
            "aggregated-expenditure": ["amount", "id", "admin", "cofog"],
            "transactional-expenditure": ["amount", "id", "admin",
                                          "date", "supplier"],
            "aggregated-revenue": ["amount", "id", "gfsmRevenue"],
            "transactional-revenue": ["amount", "id", "gfsmRevenue"]
            }

        header_errs = []
        for header in field_requirements[type]:
            if header not in self.headers:
                header_errs.append(header)
        if header_errs:
            raise AssertionError("CSV headers incorrect for type " + type
                    + ". Missing:\n\t" + ("\n\t".join(header_errs)))

        if deep:
            validator = cv.CSVValidator(self.headers)
            validator.add_header_check()
            validator.add_record_length_check()
            for header in self.headers:
                if header in field_validators:
                    validator.add_value_check(header,
                                              field_validators[header])

            validator.validate(csv.reader(self.file))


def get_type(fieldname):
    """
    Returns the right type for a field name.
    """
    if fieldname in field_types:
        return field_types[fieldname]
    return "string"


def get_fields(headers):
    """
    Generates the `fields` array for the resource metadata.

    Takes a filename.
    """
    return [{"name": header, "type": get_type(header)} for header in headers]


def cofogValidator(cofog):
    """
    Validator function.
    Checks if a string is a valid COFOG value.
    """
    p = r"^((10)|(0?[1-9]))(\.[1-9]){0,2}$"
    if re.search(p,cofog):
        return cofog
    raise ValueError("Invalid COFOG value: " + cofog)

def gfsmRevenueValidator(gfsm):
    """
    Validator function.
    Checks if a string is a valid GFSM 2001 revenue value.
    """
    p = r"^1(1(1(1|2|3)?|2|3(1|2|3|4|5|6)?|4(1(1|2|3)?|2|3|4|5(1|2)?|6)?|5|6(1|2)?)?|2(1(1|2|3|4)?|2(1|2|3)?)?|3(1(1|2)?|2(1|2)?|3(1|2)?)?|4(1(1|2|3|4)?|2(1|2|3|4)?|3|4(1|2)?|5)?)?$"
    if re.search(p,gfsm):
        return gfsm
    raise ValueError("Invalid GFSM revenue value: " + gfsm)

def gfsmExpenseValidator(gfsm):
    """
    Validator function.
    Checks if a string is a valid GFSM 2001 expenditure value.
    """
    p = r"^2(1(1(1|2)?|2(1|2)?)?|2|3|4(1|2|3)?|5(1|2)?|6(1(1|2)?|2(1|2)?|3(1|2)?)?|7(1(1|2)?|2(1|2)?|3(1|2)?)?|8(1(1|2|3|4)?|2(1|2)?)?)?$"
    if re.search(p,gfsm):
        return gfsm
    raise ValueError("Invalid GFSM expense value: " + gfsm)

# Validator for "type" fields.
typeValidator = cv.enumeration(
    "personnel",
    "non-personnel recurrent",
    "capital",
    "other"
    )

field_validators = {
    # Special fields.
    "cofog": cofogValidator,
    "gfsmExpense": gfsmExpenseValidator,
    "gfsmRevenue": gfsmRevenueValidator,
    "type": typeValidator,
    # Ordinary ol' fields.
    "admin": str,
    "adminID": str,
    "adminOrgId": str,
    "amount": float,
    "amountAdjusted": float,
    "amountBudgeted": float,
    "budgetLineItem": str,
    "code": str,
    "contractID": str,
    "date": lambda x: datetime.datetime.strptime(x, '%Y-%m-%d').date(),
    "dateAdjusted": lambda x: datetime.datetime.strptime(x, '%Y-%m-%d').date(),
    "dateReported": lambda x: datetime.datetime.strptime(x, '%Y-%m-%d').date(),
    "description": str,
    "economic": str,
    "economicID": str,
    "financialSource": str,
    "functional": str,
    "functionalID": str,
    "fund": str,
    "fundID": str,
    "geocode": str,
    "id": str,
    "invoiceID": str,
    "program": str,
    "programID": str,
    "project": str,
    "projectID": str,
    "purchaserID": str,
    "purchaserOrgID": str,
    "supplier": str,
}

field_types = {
    "amount": "number",
    "amountAdjusted": "number",
    "amountBudgeted": "number",
    "date": "date",
    "dateAdjusted": "date",
    "dateReported": "date"
}
