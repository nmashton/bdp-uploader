# -*- coding: utf-8 -*-

from app.bdp import app
import csvvalidator as cv
import datetime, time
import re
import json
import base64
import unicodecsv as csv
import os.path


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

        for header in field_requirements[type]:
            if header not in self.headers:
                raise AssertionError("CSV headers incorrect for type " + type)

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
