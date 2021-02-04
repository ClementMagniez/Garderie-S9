function htmlToPdf(id_table) {

  let pdf = new jspdf.jsPDF('p', 'pt', 'letter');

  pdf.autoTable({html:id_table});
  pdf.save();
}


