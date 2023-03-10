import logging
from schema import  Use

from src.templates_lib import PostController, ControllerEntry, AnyDict



################## Python loggers ##################
logger = logging.getLogger("back_end_test_blueprint_logger")

@PostController(
    logger,
    {
        "year": Use(int),
    }
)
def day_of_the_programmer(postData: ControllerEntry, params: AnyDict):
    """
        url: https://www.hackerrank.com/challenges/day-of-the-programmer
        Marie invented a Time Machine and wants to test it by time-traveling 
        to visit Russia on the Day of the Programmer (the 256th day of the year)
        during a year in the inclusive range from 1700 to 2700.

        From 1700 to 1917, Russia's official calendar was the Julian calendar;
        since 1919 they used the Gregorian calendar system. The transition from the Julian
        to Gregorian calendar system occurred in 1918, when the next day after January 31st was
        February 14th. This means that in 1918, February 14th was the 32nd day of the year in Russia.

        In both calendar systems, February is the only month with a variable amount of days;
        it has 29 days during a leap year, and 28 days during all other years. 
        In the Julian calendar, leap years are divisible by 4; in the Gregorian calendar,
        leap years are either of the following:

            Divisible by 400.
            Divisible by 4 and not divisible by 100.
        Given a year, y, find the date of the 256th day of that year according to
        the official Russian calendar during that year. 
        Then print it in the format dd.mm.yyyy, where dd is the two-digit day, mm is the two-digit month, and yyyy is .

        For example, the given  = 1984. 1984 is divisible by 4, so it is a leap year.
        The 256th day of a leap year after 1918 is September 12, so the answer is .
        12.09.1984

        :param year: an integer

        :return the full date of Day of the Programmer during year
        in the format dd.mm.yyyy, where dd is the two-digit day, mm is the two-digit month,
        and yyyy is y
    """
    year = postData.get("year")
    DAY_OF_PROGRAMMER = 256
    if 1700 > year or year > 2700:
        return "Error"
    if year >= 1919:
        if year % 400 == 0 or (year % 4 == 0 and year % 100 != 0):
            num_days_february = 29
        else:
            num_days_february = 28
    elif year == 1918:
            num_days_february = 15
    else:
        if year % 4 == 0:
            num_days_february = 29
        else:
            num_days_february = 28
    num_of_days_first_8_months = 215 + num_days_february
    result_day = DAY_OF_PROGRAMMER - num_of_days_first_8_months
    return f"""{result_day}.09.{year}"""