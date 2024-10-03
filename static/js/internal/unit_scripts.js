var table = ''; 
var ingredients_list = []



/**
 * Given an ingredient id, return the ingredient json object
 * Searches through a list of ingredients created in edit_recipt.html
 * @param {int} ingred_id - id of the ingredient to get
 * @returns {Object} - ingredient json object
 */
function getIngredientById(ingred_id) {
    let found_ingredient = {}
    all_ingredients.forEach(function(ingredient) {
        if (ingredient.id == ingred_id) {
            found_ingredient = ingredient;
            return
        }
    });
    return found_ingredient;
}

// This script will return the ingredients (quantity and unit) if it is found in the dict
// Only ingredients that were previously on the recipe will have data
function getQuantityForIngredient(ingredient_id, ing_dict) {
    let found_ingredient = {}
    const key = "id"
    console.log("Looking for ingredient id:", ingredient_id)
    ing_dict.forEach(function(ingredient) {
        if (ingredient.id == ingredient_id) {
            found_ingredient = ingredient;
            console.log("Found ingredient:", found_ingredient)
            return
        }
    })
    if (Object.keys(found_ingredient).length > 0) {
        return found_ingredient
    } else {
            var quantity = {quantity: 0, unit: "Item"};
            console.log("Didn't find ingredient:", quantity)
            return quantity
    }
}


function getSelected(ing_dict) {

    // Doing this enables us to show/hide the modal and reserve its data
    // TODO: THIS WILL NOT ALLOW USERS TO UPDATE INGREDIENTS ONCE ADD SAVE HAS BEEN PRESSED

    // Get the ingredients selected from the dropdown
    const values = $('#ingredients').val();

    console.log("Running getSelected(), and wiping modal")
    console.log("ing_dict:", ing_dict)
    console.log("\nvalues:", values)

    var table = '';


    const option_list = '<option value="item">Item</option> <option value="cup">Cup</option> <option value="pound">Pound</option> <option value="ounce">Ounce</option> <option value="tbsp">Tbsp</option> <option value="tsp">Tsp</option>'

    // Build the table

    // We don't really know IF A NEW INGREDIENT WAS PICKED
    // A user could have selected a new ingredient, so we might not have a quantity for each ingredient

    table += '<table class="table"> <thead> <tr> <th scope="col">Ingredient</th> <th scope="col">Quantity</th> <th scope="col">Unit</th> </tr> </thead> <tbody>'
    values.forEach(function(ing_id) {
        unitless_ingredient = getIngredientById(ing_id);
        unit_ingredient = getQuantityForIngredient(ing_id, ing_dict);
        table += '<tr class="ing-qty-row" data-ing-id="' + unitless_ingredient.id + '"> <td>' + unitless_ingredient.name + '</td>'
        table += '<td>' + '<input type="number" value=' + unit_ingredient.quantity + '></td>'
        table += '<td> <select id=' + unitless_ingredient.id + '_unit' + '>' + option_list + ' </select> </td>'
        table += '</tr>'
    });
    table += '</tbody> </table>'

    // Send this value to the Modal
    document.getElementById("ingredients_list").innerHTML = table
}

