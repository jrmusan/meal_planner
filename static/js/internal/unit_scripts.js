var table = ''; 
var ingredients_list = [];

/**
 * Given an ingredient id, return the ingredient json object
 * Searches through all_ingredients provided in window.createPage config
 * @param {int} ingred_id - id of the ingredient to get
 * @returns {Object} - ingredient json object
 */
function getIngredientById(ingred_id) {
    const cfg = window.createPage || {};
    const all_ingredients = cfg.all_ingredients || [];
    let found_ingredient = {};
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
    ing_dict.forEach(function(ingredient) {
        if (ingredient.id == ingredient_id) {
            found_ingredient = ingredient;
            return
        }
    })
    if (Object.keys(found_ingredient).length > 0) {
        return found_ingredient
    } else {
            var quantity = {quantity: 1, unit: "Item"};
            return quantity
    }
}

function getUnitForIngredient(unit_ingredient) {

    if (unit_ingredient.unit == "item") {
        return '<option value="item" selected>Item</option> <option value="cup">Cup</option> <option value="pound">Pound</option> <option value="ounce">Ounce</option> <option value="tbsp">Tbsp</option> <option value="tsp">Tsp</option>'
    }
    if (unit_ingredient.unit == "cup") {
        return '<option value="item">Item</option> <option value="cup" selected>Cup</option> <option value="pound">Pound</option> <option value="ounce">Ounce</option> <option value="tbsp">Tbsp</option> <option value="tsp">Tsp</option>'
    }
    if (unit_ingredient.unit == "pound") {
        return '<option value="item">Item</option> <option value="cup">Cup</option> <option value="pound" selected>Pound</option> <option value="ounce">Ounce</option> <option value="tbsp">Tbsp</option> <option value="tsp">Tsp</option>'
    }
    if (unit_ingredient.unit == "ounce") {
        return '<option value="item">Item</option> <option value="cup">Cup</option> <option value="pound">Pound</option> <option value="ounce" selected>Ounce</option> <option value="tbsp">Tbsp</option> <option value="tsp">Tsp</option>'
    }
    if (unit_ingredient.unit == "tbsp") {
        return '<option value="item">Item</option> <option value="cup">Cup</option> <option value="pound">Pound</option> <option value="ounce">Ounce</option> <option value="tbsp" selected>Tbsp</option> <option value="tsp">Tsp</option>'
    }
    if (unit_ingredient.unit == "tsp") {
        return '<option value="item">Item</option> <option value="cup">Cup</option> <option value="pound">Pound</option> <option value="ounce">Ounce</option> <option value="tbsp">Tbsp</option> <option value="tsp" selected>Tsp</option>'
    } else{
        return '<option value="item">Item</option> <option value="cup">Cup</option> <option value="pound">Pound</option> <option value="ounce">Ounce</option> <option value="tbsp">Tbsp</option> <option value="tsp">Tsp</option>'
    }


}


function getSelected(ing_dict) {

    // Doing this enables us to show/hide the modal and reserve its data

    // Get the ingredients selected from the dropdown
    const values = $('#ingredients').val();

    console.log("Running getSelected(), and wiping modal")

    var table = '';

    // Build data for the modal
    // All ingredients need to be included, new ingredients will have a quantity of 1.
    table += '<table class="table"> <thead> <tr> <th scope="col">Ingredient</th> <th scope="col">Quantity</th> <th scope="col">Unit</th> </tr> </thead> <tbody>'
    values.forEach(function(ing_id) {
        unitless_ingredient = getIngredientById(ing_id);
        unit_ingredient = getQuantityForIngredient(ing_id, ing_dict);
        selected_unit_ingredient = getUnitForIngredient(unit_ingredient);
        table += '<tr class="ing-qty-row" data-ing-id="' + unitless_ingredient.id + '"> <td>' + unitless_ingredient.name + '</td>'
        table += '<td>' + '<input type="number" value=' + unit_ingredient.quantity + ' style="width: 70px; max-width: 70px;" class="form-control form-control-sm"></td>'
        table += '<td> <select id=' + unitless_ingredient.id + '_unit' + ' class="form-control form-control-sm">' + selected_unit_ingredient + ' </select> </td>'
        table += '</tr>'
    });
    table += '</tbody> </table>'

    // Send this value to the Modal
    document.getElementById("ingredients_list").innerHTML = table
}

