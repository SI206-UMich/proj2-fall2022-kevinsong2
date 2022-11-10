from xml.sax import parseString
from bs4 import BeautifulSoup
import re
import os
import csv
import unittest
# Partners: Alex Chuang Alex Mah


def get_listings_from_search_results(html_file):
    """
    Write a function that creates a BeautifulSoup object on html_file. Parse
    through the object and return a list of tuples containing:
     a string of the title of the listing,
     an int of the cost to rent for one night,
     and a string of the listing id number
    in the format given below. Make sure to turn costs into ints.

    The listing id is found in the url of a listing. For example, for
        https://www.airbnb.com/rooms/1944564
    the listing id is 1944564.
.

    [
        ('Title of Listing 1', 'Cost 1', 'Listing ID 1'),  # format
        ('Loft in Mission District', 210, '1944564'),  # example
    ]
    """
    list = []
    file = open(html_file, 'r')
    content = file.read()
    soup = BeautifulSoup(content, 'html.parser')
    file.close()
    names = []
    costs = []
    ids = []
    for tag in soup.find_all(attrs={"class" : "t1jojoys dir dir-ltr"}):
        name = tag.text
        names.append(name)

    for tag in soup.find_all(attrs={"class" : "_tyxjp1"}):
        cost = tag.text[1:]
        costs.append(int(cost))
        
    for tag in soup.find_all(attrs={"itemprop" : "url"}): 
        url = tag["content"]
        pattern = r"(\d+)"
        id = re.findall(pattern, url)
        ids.append(id[0])
    
    for i in range(len(names)):
        tuple_list = []
        tuple_list.append(names[i])
        tuple_list.append(costs[i])
        tuple_list.append(ids[i])
        tup = tuple(tuple_list)
        list.append(tup)

    # print(list)
    return list


def get_listing_information(listing_id):
    """
    Write a function to return relevant information in a tuple from an Airbnb listing id.
    NOTE: Use the static files in the html_files folder, do NOT send requests to the actual website.
    Information we're interested in:
        string - Policy number: either a string of the policy number, "Pending", or "Exempt"
            This field can be found in the section about the host.
            Note that this is a text field the lister enters, this could be a policy number, or the word
            "pending" or "exempt" or many others. Look at the raw data, decide how to categorize them into
            the three categories.
        string - Place type: either "Entire Room", "Private Room", or "Shared Room"
            Note that this data field is not explicitly given from this page. Use the
            following to categorize the data into these three fields.
                "Private Room": the listing subtitle has the word "private" in it
                "Shared Room": the listing subtitle has the word "shared" in it
                "Entire Room": the listing subtitle has neither the word "private" nor "shared" in it
        int - Number of bedrooms
.
    (
        policy number,
        place type,
        number of bedrooms
    )
    """
    list2 = []
    for filename in os.listdir("html_files/"):
        match = re.search(listing_id, filename)
        if match:
            foundfile = filename
    file = open("html_files/" + foundfile)
    content = file.read()
    soup = BeautifulSoup(content, 'html.parser')
    file.close()

    for tag in soup.find(attrs={"class" : "f19phm7j dir dir-ltr"}):
        policy = tag.text
        res = policy.split(':')[-1]
        if (bool(re.search("[Pp]ending", res))):
            list2.append("Pending")
        elif (bool(re.search("needed", res))):
            list2.append("Exempt")
        else:
            list2.append(res)

    for tag in soup.find(attrs={"class" : "_14i3z6h"}):
        placeType = tag.text
        res = placeType.split(" ")[0]
        if res == "Private":
            list2.append("Private Room")
        elif res == "Entire":
            list2.append("Entire Room")
        else:
            list2.append("Shared Room")
    
    for tag in soup.find(attrs={"class" : "lgx66tx dir dir-ltr"}).find_all("span")[5]:
        if tag == "Studio":
            list2.append(1)
        else:
            numBeds = tag.split(" ")[0]
            list2.append(int(numBeds))

    rel_info = tuple(list2[1:])
    # print(rel_info)
    return rel_info


def get_detailed_listing_database(html_file):
    """
    Write a function that calls the above two functions in order to return
    the complete listing information using the functions you’ve created.
    This function takes in a variable representing the location of the search results html file.
    The return value should be in this format:


    [
        (Listing Title 1,Cost 1,Listing ID 1,Policy Number 1,Place Type 1,Number of Bedrooms 1),
        (Listing Title 2,Cost 2,Listing ID 2,Policy Number 2,Place Type 2,Number of Bedrooms 2),
        ...
    ]
    """
    det_list = []
    list = get_listings_from_search_results(html_file)
    for item in list:
        tup = get_listing_information(item[2])
        new_tup = item + tup
        det_list.append(new_tup)
    # print(det_list)
    return det_list


def write_csv(data, filename):
    """
    Write a function that takes in a list of tuples (called data, i.e. the
    one that is returned by get_detailed_listing_database()), sorts the tuples in
    ascending order by cost, writes the data to a csv file, and saves it
    to the passed filename. The first row of the csv should contain
    "Listing Title", "Cost", "Listing ID", "Policy Number", "Place Type", "Number of Bedrooms",
    respectively as column headers. For each tuple in data, write a new
    row to the csv, placing each element of the tuple in the correct column.

    When you are done your CSV file should look like this:

    Listing Title,Cost,Listing ID,Policy Number,Place Type,Number of Bedrooms
    title1,cost1,id1,policy_number1,place_type1,num_bedrooms1
    title2,cost2,id2,policy_number2,place_type2,num_bedrooms2
    title3,cost3,id3,policy_number3,place_type3,num_bedrooms3
    ...

    In order of least cost to most cost.

    This function should not return anything.
    """
    sorted_tuples = sorted(data, key=lambda x: x[1])
    headers = ['Listing Title', 'Cost', 'Listing ID', 'Policy Number', 'Place Type', 'Number of Bedrooms']
    with open(filename, 'w') as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        for tup in sorted_tuples:
            writer.writerow(tup)
    file.close()


def check_policy_numbers(data):
    """
    Write a function that takes in a list of tuples called data, (i.e. the one that is returned by
    get_detailed_listing_database()), and parses through the policy number of each, validating the
    policy number matches the policy number format. Ignore any pending or exempt listings.
    Return the listing numbers with respective policy numbers that do not match the correct format.
        Policy numbers are a reference to the business license San Francisco requires to operate a
        short-term rental. These come in two forms, where # is a number from [0-9]:
            20##-00####STR
            STR-000####
    .
    Return value should look like this:
    [
        listing id 1,
        listing id 2,
        ...
    ]

    """
    pass


def extra_credit(listing_id):
    """
    There are few exceptions to the requirement of listers obtaining licenses
    before listing their property for short term leases. One specific exception
    is if the lister rents the room for less than 90 days of a year.

    Write a function that takes in a listing id, scrapes the 'reviews' page
    of the listing id for the months and years of each review (you can find two examples
    in the html_files folder), and counts the number of reviews the apartment had each year.
    If for any year, the number of reviews is greater than 90 (assuming very generously that
    every reviewer only stayed for one day), return False, indicating the lister has
    gone over their 90 day limit, else return True, indicating the lister has
    never gone over their limit.
    """
    pass


class TestCases(unittest.TestCase):

    def test_get_listings_from_search_results(self):
        # call get_listings_from_search_results("html_files/mission_district_search_results.html")
        # and save to a local variable
        listings = get_listings_from_search_results("html_files/mission_district_search_results.html")
        # check that the number of listings extracted is correct (20 listings)
        self.assertEqual(len(listings), 20)
        # check that the variable you saved after calling the function is a list
        self.assertEqual(type(listings), list)
        # check that each item in the list is a tuple
        for item in listings:
            self.assertEqual(type(item), tuple)

        # check that the first title, cost, and listing id tuple is correct (open the search results html and find it)
        file = open("html_files/mission_district_search_results.html", 'r')
        content = file.read()
        file.close()
        soup = BeautifulSoup(content, 'html.parser')
        s1 = soup.find(attrs={"class" : "t1jojoys dir dir-ltr"})
        name = s1.text
        s2 = soup.find(attrs={"class" : "_tyxjp1"})
        cost = int(s2.text[1:])
        s3 = soup.find(attrs={"itemprop" : "url"})
        id = re.search("(\d+)", s3["content"])
        self.assertEqual(listings[0][0], name)
        self.assertEqual(listings[0][1], cost)
        self.assertEqual(listings[0][2], id.group())

        # check that the last title is correct (open the search results html and find it)
        file = open("html_files/mission_district_search_results.html", 'r')
        content = file.read()
        file.close()
        soup = BeautifulSoup(content, 'html.parser')
        s1 = soup.find_all(attrs={"class" : "t1jojoys dir dir-ltr"})
        name = s1.pop().text
        s2 = soup.find_all(attrs={"class" : "_tyxjp1"})
        cost = int(s2.pop().text[1:])
        s3 = soup.find_all(attrs={"itemprop" : "url"})
        id = re.search("(\d+)", s3.pop()["content"])
        self.assertEqual(listings[-1][0], name)
        self.assertEqual(listings[-1][1], cost)
        self.assertEqual(listings[-1][2], id.group())

    def test_get_listing_information(self):
        html_list = ["1623609",
                     "1944564",
                     "1550913",
                     "4616596",
                     "6600081"]
        # call get_listing_information for i in html_list:
        listing_informations = [get_listing_information(id) for id in html_list]
        # check that the number of listing information is correct (5)
        self.assertEqual(len(listing_informations), 5)
        for listing_information in listing_informations:
            # check that each item in the list is a tuple
            self.assertEqual(type(listing_information), tuple)
            # check that each tuple has 3 elements
            self.assertEqual(len(listing_information), 3)
            # check that the first two elements in the tuple are string
            self.assertEqual(type(listing_information[0]), str)
            self.assertEqual(type(listing_information[1]), str)
            # check that the third element in the tuple is an int
            self.assertEqual(type(listing_information[2]), int)
        # check that the first listing in the html_list has policy number 'STR-0001541'
        self.assertEqual(listing_informations[0][0], "STR-0001541")

        # check that the last listing in the html_list is a "Private Room"
        self.assertEqual(listing_informations[-1][1], "Private Room")

        # check that the third listing has one bedroom
        self.assertEqual(listing_informations[2][2], 1)

    def test_get_detailed_listing_database(self):
        # call get_detailed_listing_database on "html_files/mission_district_search_results.html"
        # and save it to a variable
        detailed_database = get_detailed_listing_database("html_files/mission_district_search_results.html")
        # check that we have the right number of listings (20)
        self.assertEqual(len(detailed_database), 20)
        for item in detailed_database:
            # assert each item in the list of listings is a tuple
            self.assertEqual(type(item), tuple)
            # check that each tuple has a length of 6
            self.assertEqual(len(item), 6)

        # check that the first tuple is made up of the following:
        # 'Loft in Mission District', 210, '1944564', '2022-004088STR', 'Entire Room', 1
        following = ('Loft in Mission District', 210, '1944564', '2022-004088STR', 'Entire Room', 1)
        self.assertEqual(detailed_database[0], following)

        # check that the last tuple is made up of the following:
        # 'Guest suite in Mission District', 238, '32871760', 'STR-0004707', 'Entire Room', 1
        tup = ('Guest suite in Mission District', 238, '32871760', 'STR-0004707', 'Entire Room', 1)
        self.assertEqual(detailed_database[-1], tup)

    def test_write_csv(self):
        # call get_detailed_listing_database on "html_files/mission_district_search_results.html"
        # and save the result to a variable
        detailed_database = get_detailed_listing_database("html_files/mission_district_search_results.html")
        # call write csv on the variable you saved
        write_csv(detailed_database, "test.csv")
        # read in the csv that you wrote
        csv_lines = []
        with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'test.csv'), 'r') as f:
            csv_reader = csv.reader(f)
            for i in csv_reader:
                csv_lines.append(i)
        # check that there are 21 lines in the csv
        self.assertEqual(len(csv_lines), 21)
        # check that the header row is correct
        header = ['Listing Title', 'Cost', 'Listing ID', 'Policy Number', 'Place Type', 'Number of Bedrooms']
        self.assertEqual(csv_lines[0], header)
        # check that the next row is Private room in Mission District,82,51027324,Pending,Private Room,1
        row1 = ['Private room in Mission District', '82', '51027324', 'Pending', 'Private Room', '1']
        self.assertEqual(csv_lines[1], row1)
        # check that the last row is Apartment in Mission District,399,28668414,Pending,Entire Room,2
        last_row = ['Apartment in Mission District', '399', '28668414', 'Pending', 'Entire Room', '2']
        self.assertEqual(csv_lines[-1], last_row)

    def test_check_policy_numbers(self):
        # call get_detailed_listing_database on "html_files/mission_district_search_results.html"
        # and save the result to a variable
        detailed_database = get_detailed_listing_database("html_files/mission_district_search_results.html")
        # call check_policy_numbers on the variable created above and save the result as a variable
        invalid_listings = check_policy_numbers(detailed_database)
        # check that the return value is a list
        self.assertEqual(type(invalid_listings), list)
        # check that there is exactly one element in the string

        # check that the element in the list is a string

        # check that the first element in the list is '16204265'
        pass


if __name__ == '__main__':
    database = get_detailed_listing_database("html_files/mission_district_search_results.html")
    write_csv(database, "airbnb_dataset.csv")
    check_policy_numbers(database)
    unittest.main(verbosity=2)
