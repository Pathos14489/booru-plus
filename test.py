from booruplus import BooruPlus

booru = BooruPlus()

# booru.scrape()  # scrape the booru and make sure it's up to date -- If it's up to date, this will only make 1 request to get the number of pages, 
                # and then it will check every page to see if it's up to date. If it's not up to date, it will then only scrape the pages that are not up to date. 
                # So 11 requests total for a 10 page booru. Could probably be slightly more efficient, but don't give enough of a fuck.
