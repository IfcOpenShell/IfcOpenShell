// PRICED BILL OF QUANTITIES TEMPLATE
// author: carlo pavan
// year: 2025


// custom cell styles
#let total-cell-style = (stroke: (top: 0.25pt + gray))



#let root-cost-cell-style = (
  stroke: (bottom: (thickness: 0.4pt, dash: "dotted")), 
  fill: gray.transparentize(90%),
  align: bottom
)



#let template_fonts = ("Liberation Sans", "Roboto", "Arial", "Calibri")



#let euro(num) = {
  str(calc.round(float(num), digits: 2)) + " €"
}



#let bill_of_quantities_table = table(
  columns: (18mm,54mm, 12mm,12mm,12mm,12mm, 20mm, 20mm, 25mm),
    rows: (6mm, 248mm),
    align: (center, left, center, center, center, center, center, center, center),
    stroke: (x, y) => (
      left: if x == 0 { 1pt } else { 0.25pt },
      right: 1pt,
      top: 1pt,
      bottom: 1pt
    ),
    [Hierarchy], [Description], [n°],[l],[w],[h/w], [Quantity], [Rate], [Total]
  )



#let schedule_of_rates_table = table(
  columns: (30mm,130mm, 25mm),
    rows: (6mm, 248mm),
    align: (center, left, center),
    stroke: (x, y) => (
      left: if x == 0 { 1pt } else { 0.25pt },
      right: 1pt,
      top: 1pt,
      bottom: 1pt
    ),
    [Identification], [Description], [Rate]
  )


  
#let summary_table = table(
  columns: (18mm,107mm, 30mm, 30mm),
  rows: (6mm, 248mm),
  align: (center, left, center, center, center, center, center, center, center),
  stroke: (x, y) => (
    left: if x == 0 { 1pt } else { 0.25pt },
    right: 1pt,
    top: 1pt,
    bottom: 1pt
  ),
  text(size: 8pt)[Hierarchy],
  text(size: 8pt)[Description], 
  text(size: 8pt)[Sub Total], 
  text(size: 8pt)[Total]
)



  
#let format_table = (
  "SCHEDULEOFRATES": schedule_of_rates_table,
  "PRICEDBILLOFQUANTITIES" : bill_of_quantities_table,
  "UNPRICEDBILLOFQUANTITIES" : bill_of_quantities_table,
  "SUMMARY" : summary_table
)



#let unit_map = (
  "METRE": "m",
  "SQUARE_METRE": "m²",
  "m2": "m²",
  "CUBIC_METRE": "m³",
  "m3": "m³",
  "VOLUMEUNIT / CUBIC_METRE": "m³",
  "KILOGRAM": "kg",
  // add more mappings as needed
)



#let format-decimal(num, places: 2) = {
  let rounded = calc.round(num, digits: places)
  let str-num = str(rounded)
  
  // Split into integer and decimal parts
  let parts = str-num.split(".")
  let integer-part = parts.at(0)
  let decimal-part = parts.at(1, default: "")
  
  // Add thousand separators to integer part
  let formatted-integer = ""
  let chars = integer-part.clusters().rev()
  for (i, char) in chars.enumerate() {
    if i > 0 and calc.rem(i, 3) == 0 {
      formatted-integer = "'" + formatted-integer
    }
    formatted-integer = char + formatted-integer
  }
  
  // Ensure decimal part has correct number of places
  decimal-part = decimal-part + "0" * (places - decimal-part.len())
  
  formatted-integer + "." + decimal-part
}



#let arrange_summary_row(row, options) = {
  let name = strong(upper(row.at("Name")))
  let description = [#par(justify: true, text(8pt, row.at("Description", default: "")))]
  let total = if row.at("RateSubtotal") == "" {0.0} else {float(row.at("RateSubtotal"))}
  if row.at("ItemIsASum") == "True" {   
    if row.at("Index") == "1" {
      // ROOT COST
      (
        strong[#row.at("Hierarchy")],
        name,
        [],
        if options.at("should_print_rates") {
          strong[#format-decimal(float(row.at("TotalPrice")), places: 2)]
        } else {
        }
      )
    } else {
      // SUB-SECTION
      ( 
        row.at("Hierarchy"),
        table.cell(inset: (left: int(row.at("Index"))*2.5mm))[#upper(row.at("Name"))],
        if options.at("should_print_rates") {
          format-decimal(float(row.at("TotalPrice")), places: 2)
        } else {
          []
        }
          ,
        [],
      )
    }
  } else {
    ()
  }
}



#let arrange_bill_of_quantity_row(row, options) = {
  if row.at("ItemIsASum") == "True" {
    // SECTION (Parent Cost Item)
    if options.at("nested_structure_depth") == 0 or int(row.at("Index")) <= options.at("nested_structure_depth") {
      let name = strong(upper(row.at("Name")))
      let description = [#par(justify: true, text(8pt, row.at("Description", default: "")))]
      let total_price = format-decimal(float(row.at("TotalPrice", default: "0.0")), places: 2)
    
      (
        [], [], [], [], [], [], [], [], [],
      )
      (
        table.cell(..root-cost-cell-style)[#row.at("Hierarchy")],
        table.cell(..root-cost-cell-style)[#strong(upper(row.at("Name"))) #linebreak() #row.at("Description", default:"")],
        table.cell(..root-cost-cell-style)[],      
        table.cell(..root-cost-cell-style)[],
        table.cell(..root-cost-cell-style)[],
        table.cell(..root-cost-cell-style)[],
        table.cell(..root-cost-cell-style)[],
        table.cell(..root-cost-cell-style)[],
        if options.at("should_print_rates") == true {
          table.cell(..root-cost-cell-style)[#strong(total_price)]
        } else{
          table.cell(..root-cost-cell-style)[]
        },
      ) 
    } else {
      ()
    }
    
  } else {
    // COST ITEM
    let name = "" 
    if row.at("Name") == "" {
      name = strong(upper("Unnamed Cost Item"))
    } else {
      name = strong(upper(row.at("Name")))
    }
    let identification = ""
    if options.at("should_print_cost_ids") == true and row.at("Identification") != "" {
      identification = linebreak() + row.at("Identification")
    } else {
      identification = ""
    }
    let description = "" 
    if options.at("should_print_description") == true and row.at("Description") != "" {
      description = [#par(justify: true, text(8pt, row.at("Description", default: "")))]
    } else {
      description = ""
    }
    let unit = table.cell(align: right)[Sum #unit_map.at(row.at("Unit"), default: "")]
    let quant = if row.at("Quantity") == "" {0.0} else {
      format-decimal(float(row.at("Quantity")))}
    let rate = if row.at("RateSubtotal") == "" {0.0} else {
      format-decimal(float(row.at("RateSubtotal")))}
    let total = if row.at("Quantity") == "" {0.0} else {
      format-decimal(float(row.at("Quantity")) * float(row.at("RateSubtotal")), places: 2)}
    
    (
      row.at("Hierarchy"),
      name + identification + description,
      [],
      [],
      [],
      [],
      [],
      [],
      [],
    )
    if row.at("Quantities") != "" and options.at("should_print_each_quantity") {
      let json_str = row.at("Quantities")
      let quantites = json.decode(json_str)
      for quantity in quantites {
            (
            [],
            if quantity.at(0) == "Unnamed" {[quantity]} else {quantity.at(0)},
            [],
            [],
            [],
            [],
            format-decimal(quantity.at(1)),
            [],
            [],
        )
      }
    }
    if options.at("should_print_rates") == true {
      (
        [],
        unit,
        [],
        [],
        [],
        [],
        table.cell(..total-cell-style, align: right + bottom)[#quant],
        table.cell(..total-cell-style, align: right + bottom)[#rate],
        table.cell(..total-cell-style, align: right + bottom)[#total],
      )
    } else {
      (
        [],
        unit,
        [],
        [],
        [],
        [],
        table.cell(..total-cell-style, align: right + bottom)[#quant],
        [.................],
        [.......................],
      )
    }
  }
}




#let arrange_schedule_of_rates_row(row, options) = {
  let name = strong(upper(row.at("Name")))
  let description = [#par(justify: true, text(8pt, row.at("Description", default: "")))]
  let unit = table.cell(align: right)[#unit_map.at(row.at("Unit"), default: "")]
  let rate = if row.at("RateSubtotal") == "" {0.0} else {
      format-decimal(float(row.at("RateSubtotal")))}
  if row.at("ItemIsASum") == "True" {return ()} //skip sections in schedule of rates
  (
    row.at("Identification"),
    if row.at("Identification") == "" {name + linebreak() + description} else {name + linebreak() + description},
    []
  )
  (
    [],
    table.cell(align: right+bottom)[#unit],
    table.cell(align: right+bottom)[#rate],
  )
  (
    [],[],[],
  )
}



#let create-schedule(
    path, 
    delimiter: ",", 
    type: "PRICEDBILLOFQUANTITIES",    
    options: ()
  ) = {
  if type == "PRICEDBILLOFQUANTITIES" or type == "UNPRICEDBILLOFQUANTITIES"{
    let data = csv(path, delimiter: delimiter, row-type: dictionary)
    let new_rows = data.map(item => arrange_bill_of_quantity_row(item, options))
   
    table(
      columns: (18mm,1fr, 12mm,12mm,12mm,12mm, 20mm, 20mm, 25mm),
      align: (center, left, center, center, center, center, right, right, right),
      stroke: none,
      ..new_rows.flatten()
    )

  } else if type == "SCHEDULEOFRATES" {
    // REMEMBER TO CHECK IF THE ROW IS UNIQUE
    let data = csv(path, delimiter: delimiter, row-type: dictionary)
    let new_rows = data.map(item => arrange_schedule_of_rates_row(item, options))
   
    table(
      columns: (30mm,130mm, 25mm),
      align: (center, left, right),
      stroke: none,
      ..new_rows.flatten()
    )
  }
}



#let create-summary(
    path, 
    delimiter: ",",
    options
  ) = {
  let data = csv(path, delimiter: delimiter, row-type: dictionary)
  let new_rows = data.map(item => arrange_summary_row(item, options))
  let general_total = data.filter(row => row.at("ItemIsASum") == "False") 
   .map(row => float(row.at("RateSubtotal", default: 0.0))*float(row.at("Quantity", default: 0.0)))
   .sum(default: 0.00)
  
  set text(size: 10pt)
  pad(left: 2cm)[SUMMARY:]
  
  set text(size: 8pt)
  table(
    columns: (18mm,107mm, 30mm, 30mm),
    align: (center, left, right, right),
    stroke: (x, y) => (
      left: none,
      right: none,
      top: (thickness: 0.4pt, dash: "dotted"),
      bottom:  (thickness: 0.4pt, dash: "dotted")
    ),
    ..new_rows.flatten()
  )
  
  set text(size: 10pt)
  grid(
  columns: (18mm,107mm, 30mm, 30mm),
  align: (center, right, center, right),
  inset: 1mm,
  fill: gray.transparentize(70%),
  [], strong[GENERAL TOTAL:], [],
  if options.at("should_print_rates"){[#strong(format-decimal(general_total, places: 2))]
  } else {
    []
  }
)
}



#let create-cover(
  title,
  schedule_name,
  schedule_description,
  schedule_type,    
) = {
  set page(
    numbering: none,
    margin: (top: 35mm, left: 20mm, right: 10mm),
    background: place( top + left, dx: 15mm, dy: 25mm,
      table(
        columns: 185mm,
        rows: 254mm,
        align: (center, left, center),
        stroke: 1pt        
      ) 
    ),
    footer: [
    #set text(size: 7pt, fill: gray)
    #align(right)[#linebreak()powered by IfcOpenShell]
    ]
  )
  set text(font: template_fonts, size: 12pt)
  place( bottom + left, dx: 0mm, dy: -10mm,
    grid(
      columns: (30mm, 135mm),
      gutter: 2em,
      align: top + left,
      [Title:], [*#title*],
      [Schedule:],[*#schedule_name*],
      [Schedule Type:], [#schedule_type],
      if schedule_description != "" {[Description:]},
      if schedule_description != "" {[#schedule_description]},
      [],[],
      [#datetime.today().display("[day]/[month]/[year]")],[Signed],
      [],[.................................],
    )
  )
  
    
}



#let project(
  
  schedule_path: "",
  title: "", 
  schedule_name: "",
  schedule_description: "",
  schedule_type: "",
  project_currency: str,
  nested_structure_depth: int,
  parent_to_new_page_up_to_depth: int,
  show_only_parents: bool,
  should_print_cover: bool,
  should_print_cost_ids: bool,
  should_print_description: bool,
  should_print_each_quantity: bool,
  should_print_each_cost_value: bool,
  should_print_rates: bool,
  should_print_summary: bool,
  
  body) = {   
  
  if should_print_cover {
    create-cover(
      title,
      schedule_name,
      schedule_description,
      schedule_type      
    )
    pagebreak()
    counter(page).update(n => n - 1)
  }
  
  set page(
    margin: (left: 15mm, right: 10mm, top: 35mm, bottom: 20mm),
    numbering: "1/1",
    number-align: end,
    header:[
      #set text(font: template_fonts, size: 9pt, lang: "en");
      #table(
        columns: (1fr, 2fr),
        rows: 10mm,
        stroke: none,
        inset: 0mm,
        align:(top+left, top+right),
        [#title], [#schedule_name]
      )
    ],
    footer: context [
      #grid(
        columns: (1fr, 1fr),
        align: (left, right),
        [#datetime.today().display("[day]/[month]/[year]")],
        [#counter(page).display("1/1", both: true)]
      )
    ],
    background: 
    place( top + left, dx: 15mm, dy: 25mm,
      format_table.at(schedule_type, default: bill_of_quantities_table)
    )
  )
  
  set text(font: template_fonts, size: 8pt, lang: "en");

  let options = (
    "nested_structure_depth": nested_structure_depth,
    "parent_to_new_page_up_to_depth": parent_to_new_page_up_to_depth,
    "show_only_parents": show_only_parents,
    "should_print_cost_ids": should_print_cost_ids,
    "should_print_description": should_print_description,
    "should_print_each_quantity": should_print_each_quantity,
    "should_print_each_cost_value": should_print_each_cost_value,
    "should_print_rates": should_print_rates,
  )
  
  if schedule_type == "UNPRICEDBILLOFQUANTITIES" {
    create-schedule(
      schedule_path, 
      type: "PRICEDBILLOFQUANTITIES", 
     options: options
    )
  } else if schedule_type == "SCHEDULEOFRATES" {
    create-schedule(
      schedule_path, 
      type: "SCHEDULEOFRATES", 
      options: options
    )
  } else {
    create-schedule(
      schedule_path, 
      type: "PRICEDBILLOFQUANTITIES",
      options: options
    )
  }
    
  if should_print_summary and schedule_type != "SCHEDULEOFRATES"{
    pagebreak()
    set text(font: template_fonts, size: 8pt, lang: "en");
    set page(
    background:
      place( top + left, dx: 15mm, dy: 25mm,
        format_table.at("SUMMARY")
    )
  )
    create-summary(schedule_path, options)
  }
}