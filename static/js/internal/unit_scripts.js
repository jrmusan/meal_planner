var table = ''; 
var ingredients_list = []

function getIngredientById(ingred_id) {
    let found_ingredient = {}
    all_ingredients.forEach(function(ing_json) {
        if (ing_json.id == ingred_id) {
            found_ingredient = ing_json;
            return
        }
    });
    return found_ingredient;
}

function getSelected() {

    // Doing this enables us to show/hide the modal and reserve its data
    // TODO: THIS WILL NOT ALLOW USERS TO UPDATE INGREDIENTS ONCE ADD SAVE HAS BEEN PRESSED
    if( table ) {
        $('#unitModal').modal('show');
    } else {
        
        // Get the ingredients selected from the dropdown
        const values = $('#ingredients').val();
        console.log(values)

        const option_list = '<option value="item">Item</option> <option value="cup">Cup</option> <option value="pound">Pound</option> <option value="ounce">Ounce</option> <option value="tbsp">Tbsp</option> <option value="tsp">Tsp</option>'
        
        // Build the table
        table += '<table class="table"> <thead> <tr> <th scope="col">Ingredient</th> <th scope="col">Quantity</th> <th scope="col">Unit</th> </tr> </thead> <tbody>'
        values.forEach(function(ing_id) {
            ingredient = getIngredientById(ing_id);
            table += '<tr class="ing-qty-row" data-ing-id="' + ingredient.id + '"> <td>' + ingredient.name + '</td>'
            table += '<td>' + '<input type="number" value=1></td>'
            table += '<td> <select id=' + ingredient.id + '_unit' + '>' + option_list + ' </select> </td>'
            table += '</tr>'
        }); 
        table += '</tbody> </table>'
        
        // Send this value to the Modal
        document.getElementById("ingredients_list").innerHTML = table
    }
}

