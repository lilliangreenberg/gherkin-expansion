Feature: Advanced Search and Filtering

  As a user
  I want to search and filter content efficiently
  So that I can find relevant information quickly

  Rule: Basic search must return relevant results

    Scenario: Search with single keyword
      Given the database contains 100 products
      And 15 products contain the word "laptop"
      When I search for "laptop"
      Then I should receive 15 results
      And results should be ordered by relevance
      And the search should complete in under 500ms

    Scenario: Search with multiple keywords
      Given the database contains products
      When I search for "gaming laptop 16GB"
      Then results should match all keywords
      And products with exact phrase should rank highest
      And products matching most keywords should rank next
      And products matching any keyword should rank lowest

    Scenario: Search with no results
      Given the database contains products
      When I search for "nonexistentproduct12345"
      Then I should receive 0 results
      And I should see message "No results found for 'nonexistentproduct12345'"
      And I should see suggestions for similar searches
      And I should see message "Try using different keywords"

    Scenario: Handle special characters in search query
      Given the database contains products
      When I search for "C++ programming & development"
      Then special characters should be handled correctly
      And results should include "C++" products
      And the "&" should be interpreted as "AND"

  Rule: Search must support advanced operators

    Scenario: Exact phrase search with quotes
      Given products "Red Shoes" and "Shoes Red" exist
      When I search for "\"Red Shoes\""
      Then only products with exact phrase "Red Shoes" should be returned
      And "Shoes Red" should not be in results

    Scenario: Exclude terms with minus operator
      Given products "Apple iPhone" and "Apple iPad" exist
      When I search for "Apple -iPhone"
      Then results should include "Apple iPad"
      And results should not include "Apple iPhone"

    Scenario: OR operator for alternative terms
      Given products with categories exist
      When I search for "laptop OR notebook"
      Then results should include products matching either term
      And both "laptop" and "notebook" matches should be shown

    Scenario: Wildcard search
      Given products exist
      When I search for "book*"
      Then results should include "book", "books", "bookstore", "bookmark"
      And results should match any word starting with "book"

  Rule: Filtering must narrow search results correctly

    Scenario: Apply single filter to search results
      Given I searched for "laptop" and got 50 results
      When I apply filter "brand:Dell"
      Then results should be reduced to Dell laptops only
      And the search query should be preserved
      And I should see "15 results with filters applied"

    Scenario: Apply multiple filters with AND logic
      Given I searched for "laptop" and got 50 results
      When I apply filters "brand:Dell AND price:500-1000 AND rating:4+"
      Then results should match all filter criteria
      And each filter should be visually indicated
      And I can remove individual filters

    Scenario: Filter by price range
      Given I searched for "monitor"
      When I apply price filter "$200-$500"
      Then all results should have price between $200 and $500
      And results should be sorted by relevance (not price)
      And I should see price range in filter tags

    Scenario: Filter by multiple values in same category
      Given I searched for "shirt"
      When I apply filter "size:M OR size:L"
      Then results should include both M and L sizes
      And the filter should show "Size: M, L"

    Scenario: No results after applying filters
      Given I searched for "laptop" and got 50 results
      When I apply filters that match no products
      Then I should see message "No results match these filters"
      And I should see suggestion to remove some filters
      And I should be able to clear all filters with one click

  Rule: Pagination must handle large result sets

    Scenario: Navigate through paginated results
      Given a search returns 250 results
      And page size is 25 results
      When I view search results
      Then I should see 25 results on page 1
      And I should see "Page 1 of 10"
      And I should see pagination controls

    Scenario: Jump to specific page
      Given a search returns 250 results with 25 per page
      When I click to go to page 5
      Then I should see results 101-125
      And the current page should be highlighted
      And filters and sort order should be preserved

    Scenario: Change page size
      Given I am viewing page 2 with 25 results per page
      When I change page size to 50
      Then I should see 50 results
      And I should be on page 1 (recalculated)
      And the URL should update with new page size

    Scenario: Handle edge case of last partial page
      Given a search returns 243 results
      And page size is 25
      When I navigate to page 10
      Then I should see 18 results (243 - 225)
      And "Next" button should be disabled
      And page indicator should show "Page 10 of 10"

  Rule: Sort order must work with search relevance

    Scenario: Default sort by relevance
      Given I search for "laptop gaming"
      Then results should be sorted by relevance score
      And products with both terms should rank highest
      And products with one term should rank lower

    Scenario: Sort by price ascending
      Given I searched for "headphones"
      When I sort by "Price: Low to High"
      Then results should be ordered by price ascending
      And relevance should be secondary sort criteria
      And the sort option should be highlighted

    Scenario: Sort by newest first
      Given I searched for "books"
      When I sort by "Newest"
      Then results should be ordered by publication date descending
      And today's publications should appear first

    Scenario Outline: Various sort options
      Given I searched for "shoes"
      When I sort by "<sort_option>"
      Then results should be ordered by <criteria>

      Examples:
        | sort_option           | criteria                    |
        | Price: Low to High    | price ascending             |
        | Price: High to Low    | price descending            |
        | Customer Rating       | rating descending           |
        | Newest                | date descending             |
        | Best Selling          | sales_count descending      |
        | Name: A-Z             | name ascending              |

  Rule: Search must be optimized for performance

    Scenario: Fast search response for common queries
      Given the search index is warmed up
      When I search for a common term
      Then results should return in under 300ms
      And the response time should be measured

    Scenario: Handle typos with fuzzy matching
      Given products with name "Bluetooth"
      When I search for "Blutooth" (typo)
      Then I should see results for "Bluetooth"
      And I should see message "Showing results for 'Bluetooth'"
      And I should see option "Search instead for 'Blutooth'"

    Scenario: Autocomplete suggestions
      Given I am on the search page
      When I type "lapt"
      Then I should see suggestions: "laptop", "laptop bag", "laptop stand"
      And suggestions should appear within 200ms
      And suggestions should be based on popular searches

    Scenario: Handle very large result sets efficiently
      Given a search would return 1 million results
      When I perform the search
      Then only the first 10,000 should be accessible
      And I should see message "Showing top 10,000 results"
      And I should be encouraged to use filters to narrow results

  Rule: Search must track analytics

    Scenario: Log search queries for analytics
      Given I am a logged-in user
      When I search for "wireless mouse"
      Then the query should be logged with timestamp
      And my user ID should be associated with the search
      And the number of results should be recorded

    Scenario: Track zero-result searches
      Given I am searching
      When a search returns no results
      Then the query should be flagged as zero-result
      And it should be available for analysis
      And popular zero-result queries should be reviewed

    Scenario: Track result click-through rates
      Given I performed a search with 10 results
      When I click on result number 3
      Then the click should be recorded
      And the result position should be logged
      And click-through rate should be calculated

  Rule: Search must handle concurrent requests safely

    Scenario: Handle spike in search traffic
      Given the system receives 1000 searches per second
      When the load spike occurs
      Then all searches should be processed
      And response times should remain under 1 second
      And no requests should be dropped

    Scenario: Cache popular search queries
      Given "iPhone 15" is searched 1000 times per hour
      When I search for "iPhone 15"
      Then the results should be served from cache
      And the cache should be updated every 5 minutes
      And response time should be under 100ms
