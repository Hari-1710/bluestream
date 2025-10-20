frappe.ui.form.on('Quotation', {
    refresh(frm) {
        frm.add_custom_button(__('PQD and Submittals'), function() {
            create_pqd_and_submittals(frm);
        }, __('Create'));
    }
});

function create_pqd_and_submittals(frm) {
    // Prepare default values
    let defaults = {
        quotation: frm.doc.name,
        client: frm.doc.party_name,
        project_name: frm.doc.rfq_no_project_name
    };

    // If the quotation has items, fetch the first item_code
    if (frm.doc.items && frm.doc.items.length > 0) {
        defaults.item = frm.doc.items[0].item_code; // prefill first item
    }

    // Open a new PQD and Submittals form (unsaved) with defaults
    frappe.new_doc('PQD and Submittals', defaults);
}
