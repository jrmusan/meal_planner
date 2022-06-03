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

        const option_list = '<option value="item">Item</option> <option value="cup">Cup</option> <option value="pound">Pound</option> <option value="ounce">Ounce</option> '
        
        // Build the table
        table += '<table class="table"> <thead> <tr> <th scope="col">Ingredient</th> <th scope="col">Quantity</th> <th scope="col">Unit</th> </tr> </thead> <tbody>'
        values.forEach(function(ing_id) {
            ingredient = getIngredientById(ing_id);
            table += '<tr class="ing-qty-row" data-ing-id="' + ingredient.id + '"> <td>' + ingredient.name + '</td>'
            table += '<td>' + '<input type="number"></td>'
            table += '<td> <select id=' + ingredient.id + '_unit' + '>' + option_list + ' </select> </td>'
            table += '</tr>'
        }); 
        table += '</tbody> </table>'
        
        // Send this value to the Modal
        document.getElementById("ingredients_list").innerHTML = table
    }
}

// This will gather the ingredient unit/quantities and post them
function save() {

    let ing_qt_dict_list = []
    
    // So first get all the quantites for each selected ingredient
    let ing_qt_row = $('.ing-qty-row')
    for (var row of ing_qt_row) {
        // Next for now, lets log each ingredients quantity
        let ing_id = $(row).data()['ingId']
        let ing_qty = $(row).find('input').val()
        let ing_sel = $(row).find('select').val()
        ing_qt_dict_list.push({"id": ing_id, "qt": ing_qty, "unit": ing_sel})
    }

    // Converting list of key/val pairs to a dict
    let form_data = $('form').serializeArray()
    let post_data = {} 
    form_data.forEach(function(pair) {
        post_data[pair.name] = pair.value
    })

    // Add ingredients in to the post_data
    post_data["selected_ingredients"] = ing_qt_dict_list
    // Remove un-nedded key/val
    delete post_data["ingredients"];

    post_data_string = JSON.stringify(post_data)

    $.ajax({
        type: "POST",
        url: '{{ url_for("create") }}',
        data: post_data_string,
        dataType: "json",
        success: function(response) {
            window.location.href = response.url;
        }
        });
};