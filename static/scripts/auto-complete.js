var client = algoliasearch("GD0ORI3267", "611015dbe69674be524b49c2a8983fb9");
      var index = client.initIndex('polls');
      
      
      //initialize autocomplete on search input (ID selector must match)
      autocomplete('#aa-search-input', 
      { hint: false }, { 
          source: autocomplete.sources.hits(index, {hitsPerPage: 5}),
          //value to be displayed in input control after user's suggestion selection 
          displayKey: 'question',
          //hash of templates used when rendering dataset
          templates: { 
              //'suggestion' templating function used to render a single suggestion
              suggestion: function(suggestion) {
					console.log(suggestion)
                return '<a href="/polls/' + suggestion.poll_id + '" class="search-link"><span>' + suggestion._highlightResult.question.value + '</span></a>';
              }
          }
      });
