// Extracted JS for create recipe page
(function(){
  const cfg = window.createPage || {};
  var table = '';
  var ingredients_list = [];
  const all_ingredients = cfg.all_ingredients || [];

  // Save function: collects ingredient quantities and posts JSON to server
  function save() {
    let ing_qt_dict_list = [];

    // collect quantities from .ing-qty-row
    let ing_qt_row = $('.ing-qty-row');
    for (var row of ing_qt_row) {
      let ing_id = $(row).data()['ingId'];
      let ing_qty = $(row).find('input').val();
      let ing_sel = $(row).find('select').val();
      ing_qt_dict_list.push({"id": ing_id, "qt": ing_qty, "unit": ing_sel});
    }

    // serialize form into object
    let form_data = $('form').serializeArray();
    let post_data = {};
    form_data.forEach(function(pair) { post_data[pair.name] = pair.value; });

    // Handle cuisine - if "other" is selected, use the custom input value
    if (post_data["cuisine"] === "other") {
      post_data["cuisine"] = post_data["cuisine-other"] || "";
    }
    delete post_data["cuisine-other"];

    post_data["selected_ingredients"] = ing_qt_dict_list;
    delete post_data["ingredients"];

    const post_data_string = JSON.stringify(post_data);

    $.ajax({
      type: "POST",
      url: cfg.createUrl || window.location.pathname,
      data: post_data_string,
      dataType: "json",
      success: function(response) {
        window.location.href = response.url;
      },
      error: function(response) {
        let error = (response && response.responseJSON && response.responseJSON.error) || 'Unknown error';
        alert(error);
      }
    });
  }

  // expose save globally (templates may call it)
  window.save = save;

  // track whether the Add quantities button was used
  window.addButtonPressed = window.addButtonPressed || false;

  // wire up buttons once DOM is ready
  $(function(){
    const addBtn = document.getElementById('add-quantities-btn');
    if (addBtn) {
      addBtn.addEventListener('click', function(){
        // Call the shared getSelected function (provided by unit_scripts.js)
        if (typeof getSelected === 'function') {
          getSelected(cfg.ing_dict);
        }
        window.addButtonPressed = true;
        const createBtn = document.getElementById('create');
        if (createBtn) createBtn.disabled = false;
      });
    }

    const createBtn = document.getElementById('create');
    if (createBtn) {
      createBtn.addEventListener('click', function(e){
        if (window.addButtonPressed) {
          save();
        }
      });
    }
  });

})();
