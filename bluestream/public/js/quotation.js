frappe.ui.form.on('Quotation', {
    refresh(frm) {
        // Button 1: PQD and Submittals
        frm.add_custom_button(__('PQD and Submittals'), function() {
            create_pqd_and_submittals(frm);
        }, __('Create'));

        // Button 2: Production Drawing Request
        frm.add_custom_button(__('Production Drawing Request'), function() {
            create_production_drawing_request(frm);
        }, __('Create'));
    }
});

function create_production_drawing_request(frm) {
    // Prepare default values for the new document
    let defaults = {
        quotation: frm.doc.name,
        customer_name: frm.doc.customer_name,
        project_details: frm.doc.rfq_no_project_name
    };

    // Create new doc
    frappe.model.with_doctype('Production Drawing Request', () => {
        let new_doc = frappe.model.get_new_doc('Production Drawing Request');

        // Apply defaults
        Object.assign(new_doc, defaults);

        // Add quotation items into budget table
        if (frm.doc.items && frm.doc.items.length > 0) {
            frm.doc.items.forEach(item => {
                let row = frappe.model.add_child(new_doc, 'D Request Table', 'budget_table');
                row.item_name = item.item_code;
                row.description = item.description;
                row.quantity = item.qty;
            });
        }

        // Finally open the new document
        frappe.set_route('Form', 'Production Drawing Request', new_doc.name);
    });
}


function create_pqd_and_submittals(frm) {
    // Prepare default values
    let defaults = {
        quotation: frm.doc.name,
        client: frm.doc.customer_name,
        project_name: frm.doc.rfq_no_project_name
    };

    // Open the "PQD and Submittals" form with prefilled values
    frappe.new_doc('PQD and Submittals', defaults);
}
