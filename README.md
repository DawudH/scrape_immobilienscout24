# Scrape immobilienscout24.de, and email new properties found
Finding a new apartment in the Rhine-Ruhr area is exhausting and slow. 
There are too many people in need for a nice apartment.
Many real-estate agents here work on a first-come first-serve basis. 
Some apartments are only online for a few hours until they have enough responses.
So there is a need for quick reply after a property has come online. 
Another problem with the immobilienscout website, is the filters you can use for searches. 
I was looking for an apartment with a garden, that allowed pets. Now there is a filter for the garden, 
but no filter to check if pets are allowed, making me checkout many unsuitable apartments.
Lastly, immobilienscout has an e-mail service, sending you an email when a new apartment comes online.
In my experience, this service does not send all apartments that are put on the website. 
And it is slow, it is not uncommon to receive the email 5 hours after the apartment is uploaded.

So how does this script solve all these problems for me? making me spend as little time possible looking for new apartments?
* A cron job runs the scraper every 15 minutes, based on a few basic search urls on the website.
* Properties that match my custom filters are stored in a SQLite database.
* If some of the scraped properties did not already exist in the database, an email is send to the recipients.

This script made me be the first to reply to many apartments (probably confusing quite some people how that is possible).
* 15 minutes is the maximum time between upload of apartment and email sent.
* My custom pet filter is applied, filtering all the apartments that do not allow pets.



# Installation
 - Clone the repository
 - make an environment and install the requirements (see requirements.txt)
 - Provide the start urls in the scrape_immobilienscout24/spiders/ImmobilienscoutSpider.py file. 
 These urls are basic searches on immobilienscout24.de, just follow one of the links that is now in there to have an example.
 - Provide the gmail account details in the mailer/settings.py file.
    * Make sure to allow less secure apps on google to use this feature:
    [https://myaccount.google.com/lesssecureapps](https://myaccount.google.com/lesssecureapps)
 - Provide the recipients email addresses in the mailer/settings.py file
 - To set up a cron job, make sure that the shell and path is set. Use the cron.sh bash file to run scrapy.
 See snippet of the cron table below.
 ```
 SHELL=/bin/bash
 PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/u$
 0,15,30,45 * * * * sh ~/scrape_immobilienscout24/cron.sh
 ```
 - If you just want to run the scraper once:
```
sh cron.sh
```

# Comments
The filters are now hardcoded in the spider. If you want to customize this script for your personal needs, you have to change that.
Currently I will not be making this script more generally usable. I put this script here for other people to use, or in to have an example of scrapy.


# TODO
* The log rotate does not work properly run from a cron job. For now I copied the bash script. I might change it in the future if I need it for another project.
* Make the script also work for buying properties. 