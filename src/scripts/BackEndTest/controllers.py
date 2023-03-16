import logging
from schema import  Use

from src.templates_lib import PostController, ControllerEntry, AnyDict
from collections import Counter
import math

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


@PostController(
    logger,
    {
        "bill": Use(list),
        "k": Use(int),
        "b": Use(int)
    }
)
def bon_appetit(postData: ControllerEntry, params: AnyDict):
    """
        url: https://www.hackerrank.com/challenges/bon-appetit
        Two friends Anna and Brian, are deciding how to split the bill at a dinner.
        Each will only pay for the items they consume. Brian gets the check and calculates
        Anna's portion. You must determine if his calculation is correct.

        For example, assume the bill has the following prices: bill = [2,4,6] . 
        Anna declines to eat item k = bill[2] which costs 6. If Brian calculates
        the bill correctly, Anna will pay (2+4)/2 = 3 . If he includes the 
        cost of bill[2], he will calculate (2+4+6)/2 = 6. In the second case, 
        he should refund 3 to Anna.

        :param bill: an array of integers representing the cost of each item ordered
        :param k: an integer representing the zero-based index of the item Anna doesn't eat
        :param b: the amount of money that Anna contribuited to the bill

        :return 'Bon Appetit' if the bill is fairly split otherwise, it should print the 
        integer amount of money that Brian owes Anna
    """
    bill = postData.get("bill")
    k = postData.get("k")
    b = postData.get("b")
    split_bill = sum(bill)/2
    del bill[k]
    split_bill_anna = sum(bill)/2
    if int(split_bill_anna) == b:
        return "Bon Appetit"
    return int(split_bill - split_bill_anna)


@PostController(
    logger,
    {
        "ar": Use(list),
        "n": Use(int),
    }
)
def sock_merchant(postData: ControllerEntry, params: AnyDict):
    """
        url: https://www.hackerrank.com/challenges/sock-merchant
        There is a large pile of socks that must be paired by color.
        Given an array of integers representing the color of each sock,
        determine how many pairs of socks with matching colors there are.

        For example

        n = 7
        ar = [1,2,1,2,1,3,2]
        
        There is one pair of color 1 and one of color 2.
        There are three odd socks left, one of each color. The number of pairs is 2

        :param n:int number of socks in the pile
        :param ar:list[int] the colors of each sock

        :return int the numers of pairs
    """
    ar = postData.get("ar")
    count_socks = Counter(ar)
    num_pair = 0
    for sock in count_socks:
        pair_count = math.floor(count_socks[sock] / 2)
        if pair_count > 0:
            num_pair += pair_count
    return num_pair


@PostController(
    logger,
    {
        "n": Use(int),
        "p": Use(int),
    }
)
def drawing_book(postData: ControllerEntry, params: AnyDict):
    """
        url: https://www.hackerrank.com/challenges/drawing-book
        A teacher asks the class to open their books to a page number.
        A student can either start turning pages from the front of the book
        or from the back of the book. They always turn pages one at a time.
        When they open the book, page 1 is always on the right side

        When they flip page 1, they see pages 2 and 3. Each page except 
        the last page will always be printed on both sides. The last
        page may only be printed on the front, given the length of the book.
        If the book is n pages long, and a student wants to turn to page p,
        what is the minimum number of pages to turn? 
        They can start at the beginning or the end of the book.

        Given n and p, find and print the minimum number of pages that
        must be turned in order to arrive at page p.

        For example

        n = 5
        p = 3

        If the student wants to get to page 3, they open the book to page 1, flip 1 
        page and they are on the correct page. If they open the book to the last page,
        page 5, they turn 1 page and are at the correct page. Return 1.
        

        :param n:int number pages in the book
        :param p:int the page number to turn to

        :return int the minimum number of pages to turn
    """
    n = postData.get("n")
    p = postData.get("p")
    steps_front = 0
    steps_back = 0
    last_steps_front = None
    last_steps_back = None
    back_i = n
    for i in range(1,n+1,1):
        print(i)
        if i % 2 != 0:
            if (i  == p or i-1 == p) and last_steps_front is None:
                last_steps_front = steps_front
            steps_front += 1
        if back_i % 2 == 0:
            if (back_i  == p or back_i+1 == p) and last_steps_back is None:
                last_steps_back = steps_back
            steps_back += 1
        back_i -= 1
        if last_steps_back is not None and last_steps_front is not None:
            break
    if p == 1:
        last_steps_back = steps_back
    if n == p:
        last_steps_front = steps_front
    return {"num":min([last_steps_back,last_steps_front])}

@PostController(
    logger,
    {
        "steps": Use(int),
        "path": Use(str),
    }
)
def counting_valleys(postData: ControllerEntry, params: AnyDict):
    """
        url: https://www.hackerrank.com/challenges/counting-valleys
        An avid hiker keeps meticulous records of their hikes. During
        the last hike that took exactly steps steps, for every step it was noted 
        if it was an uphill, U, or a downhill, D step. Hikes always start and 
        end at sea level, and each step up or down represents a 1 unit change 
        in altitude. We define the following terms:

        - A mountain is a sequence of consecutive steps above sea level, starting
        with a step up from sea level and ending with a step down to sea level.

        - A valley is a sequence of consecutive steps below sea level,
        starting with a step down from sea level and ending with a step up to sea level.

        Given the sequence of up and down steps during a hike, find and print the
        number of valleys walked through.

        For example

        steps = 8 path = [DDUUUUDD]

        The hiker first enters a valley 2 units deep. Then they climb out
        and up onto a mountain 2 units high. Finally, the hiker returns to 
        sea level and ends the hike.
        

        :param steps:int number of steps on the hike
        :param path:string a string describing the path

        :return int the number of valleys traversed
    """
    steps = postData.get("steps")
    path = postData.get("path")
    sea_level = 0
    valleys = 0
    for i in path:
        if i == "D"  and sea_level == 0:
            valleys += 1
        if i == "U":
            sea_level  += 1
        else:
            sea_level -= 1
    return {"msg":valleys}

@PostController(
    logger,
    {
        "steps": Use(int),
        "path": Use(str),
    }
)
def cats_and_a_mouse(postData: ControllerEntry, params: AnyDict):
    """
        url: https://www.hackerrank.com/challenges/counting-valleys
        Two cats and a mouse are at various positions on a line. 
        You will be given their starting positions. Your task is to 
        determine which cat will reach the mouse first, assuming the 
        mouse does not move and the cats travel at equal speed. If the 
        cats arrive at the same time, the mouse will be allowed to move 
        and it will escape while they fight.

        You are given q queries in the form of x, y, and z representing the respective 
        positions for cats A and B, and for mouse C. Complete the function catAndMouse to return 
        the appropriate answer to each query, which will be printed on a new line.

        - If cat A catches the mouse first, print Cat A.

        - If cat B catches the mouse first, print Cat B.

        - If both cats reach the mouse at the same time, print Mouse C as the two cats fight and mouse escapes.

        Given the sequence of up and down steps during a hike, find and print the
        number of valleys walked through.

        For example

        x = 2
        y = 5
        z = 4

        The cats are at positions 2 (Cat A) and 5 (Cat B), and the mouse is at position 4. 
        Cat B, at position 5 will arrive first since it is only  unit away while the 
        other is 1 units away. Return 'Cat B'.
        

        :param x:int Cat A position
        :param yint Cat B position
        :param z:int Mouse C position

        :return str Either 'Cat A', 'Cat B' or 'Mouse C'
    """
    x = postData.get("x")
    y = postData.get("y")
    z = postData.get("z")
    dist_cat_a = abs(x - z)
    dist_cat_b = abs(y - z)
    if dist_cat_a == dist_cat_b:
        return "Mouse C"
    if dist_cat_a > dist_cat_b:
        return "Cat B"
    else:
        return "Cat A"