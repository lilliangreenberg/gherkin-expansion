Feature: E-commerce Shopping Cart Management

  As a customer
  I want to manage items in my shopping cart
  So that I can purchase products online

  Rule: Adding items to cart must handle inventory constraints

    Scenario: Add available item to empty cart
      Given my shopping cart is empty
      And product "Laptop" has 10 units in stock
      When I add 1 unit of "Laptop" to my cart
      Then my cart should contain 1 unit of "Laptop"
      And the cart total should be $999.99

    Scenario: Add multiple items to cart
      Given my shopping cart is empty
      When I add 2 units of "Mouse" to my cart
      And I add 1 unit of "Keyboard" to my cart
      Then my cart should contain 2 items
      And the total quantity should be 3 units
      And the cart total should be calculated correctly

    Scenario: Prevent adding more items than available stock
      Given product "Limited Edition Watch" has 2 units in stock
      When I attempt to add 5 units of "Limited Edition Watch" to my cart
      Then the add should fail with message "Only 2 units available in stock"
      And my cart should remain unchanged

    Scenario: Add item that is out of stock
      Given product "Sold Out Item" has 0 units in stock
      When I attempt to add 1 unit of "Sold Out Item" to my cart
      Then the add should fail with message "Product is currently out of stock"
      And I should be offered option to add to wishlist

  Rule: Cart quantity updates must validate constraints

    Scenario: Increase quantity of existing cart item
      Given my cart contains 2 units of "Headphones"
      And product "Headphones" has 10 units in stock
      When I increase the quantity to 5 units
      Then my cart should contain 5 units of "Headphones"
      And the cart total should be updated accordingly

    Scenario: Decrease quantity of cart item
      Given my cart contains 5 units of "USB Cable"
      When I decrease the quantity to 2 units
      Then my cart should contain 2 units of "USB Cable"
      And the cart total should be updated accordingly

    Scenario: Remove item by setting quantity to zero
      Given my cart contains 3 units of "Phone Case"
      When I set the quantity to 0
      Then "Phone Case" should be removed from my cart
      And my cart should recalculate the total

    Scenario: Prevent quantity update exceeding maximum per order
      Given my cart contains 5 units of "Popular Item"
      And "Popular Item" has a maximum purchase limit of 10 units per order
      When I attempt to increase quantity to 15 units
      Then the update should fail with message "Maximum 10 units allowed per order"
      And the quantity should remain at 5 units

  Rule: Cart must handle pricing and discounts correctly

    Scenario: Apply valid discount code
      Given my cart total is $100.00
      And I have a discount code "SAVE20" for 20% off
      When I apply discount code "SAVE20"
      Then the discount should be applied
      And my cart total should be $80.00
      And the discount should be shown as "-$20.00"

    Scenario: Reject invalid discount code
      Given my cart total is $100.00
      When I apply discount code "INVALID"
      Then the discount should not be applied
      And I should receive message "Invalid discount code"
      And my cart total should remain $100.00

    Scenario: Reject expired discount code
      Given I have a discount code "EXPIRED10" that expired yesterday
      When I apply discount code "EXPIRED10"
      Then the discount should not be applied
      And I should receive message "This discount code has expired"

    Scenario: Apply discount code with minimum purchase requirement
      Given my cart total is $25.00
      And discount code "SAVE50" requires minimum purchase of $50.00
      When I apply discount code "SAVE50"
      Then the discount should not be applied
      And I should receive message "Minimum purchase of $50.00 required"

    Scenario: Only one discount code can be applied
      Given my cart has discount code "SAVE10" applied
      When I attempt to apply discount code "SAVE20"
      Then the new discount should not be applied
      And I should receive message "Only one discount code allowed per order"
      And discount "SAVE10" should remain active

  Rule: Cart persistence must work across sessions

    Scenario: Cart persists after logout for registered user
      Given I am logged in as a registered user
      And my cart contains 3 items
      When I logout
      And I login again
      Then my cart should still contain the same 3 items
      And the cart total should be preserved

    Scenario: Guest cart merges with user cart on login
      Given I am browsing as a guest
      And my guest cart contains "Item A" and "Item B"
      When I login to my account which has "Item C" in cart
      Then my cart should contain "Item A", "Item B", and "Item C"
      And duplicate items should have quantities combined

    Scenario: Guest cart expires after 30 days
      Given I created a guest cart 30 days ago
      When I return to the site with the same session
      Then my cart should be empty
      And I should see message "Your cart has expired"

  Rule: Cart must handle concurrent updates safely

    Scenario: Handle stock depletion between add and checkout
      Given product "Hot Item" has 1 unit in stock
      And my cart contains 1 unit of "Hot Item"
      And another customer purchases the last unit
      When I proceed to checkout
      Then I should receive message "Hot Item is no longer available"
      And the item should be removed from my cart
      And I should be offered similar product recommendations

    Scenario: Handle price changes before checkout
      Given my cart contains "Widget" priced at $50.00
      And the price of "Widget" changes to $45.00
      When I view my cart
      Then I should see the updated price of $45.00
      And I should see a message "Price updated since adding to cart"

    Scenario: Prevent race condition on quantity updates
      Given my cart contains 5 units of "Item"
      And product "Item" has 10 units in stock
      When I attempt to increase to 8 units
      And simultaneously another customer adds 7 units to their cart
      Then one of the requests should succeed
      And the other should receive message about insufficient stock
      And the total allocated units should not exceed 10

  Rule: Cart must enforce business rules

    Scenario: Minimum order value requirement
      Given the store requires minimum order of $25.00
      And my cart total is $15.00
      When I attempt to proceed to checkout
      Then checkout should be blocked
      And I should see message "Minimum order value is $25.00 (current: $15.00)"

    Scenario: Maximum cart items limit
      Given the cart allows maximum 50 unique items
      And my cart contains 50 different items
      When I attempt to add a new item
      Then the add should fail with message "Cart can contain maximum 50 different items"

    Scenario: Restricted items cannot be combined
      Given product "Alcohol" has age restriction
      And product "Gift Card" cannot be combined with other items
      And my cart contains "Alcohol"
      When I attempt to add "Gift Card" to cart
      Then the add should fail with message "Gift Cards must be purchased separately"

    Scenario: Calculate shipping based on cart weight
      Given my cart contains items with total weight of 25 lbs
      And shipping rate is $5 per 10 lbs
      When I view shipping estimate
      Then the shipping cost should be $15.00
      And I should see message about weight-based shipping
