import jsPDF from 'jspdf';

describe('Reservation PDF compatibility', () => {
  it('creates an A4 PDF containing a ticket image and heading', () => {
    const canvas = document.createElement('canvas');
    canvas.width = 100;
    canvas.height = 50;
    const context = canvas.getContext('2d')!;
    context.fillStyle = '#ffffff';
    context.fillRect(0, 0, 100, 50);
    context.fillStyle = '#000000';
    context.fillText('Reserva 123', 5, 25);

    const pdf = new jsPDF('p', 'mm', 'a4');
    pdf.setFontSize(18);
    pdf.text('Hoteleriapp - Ticket de Reserva', 105, 15, { align: 'center' });
    pdf.addImage(canvas.toDataURL('image/png'), 'PNG', 0, 25, 210, 105);
    const output = pdf.output();
    expect(output.startsWith('%PDF-')).toBeTrue();
    expect(output).toContain('Hoteleriapp - Ticket de Reserva');
    expect(pdf.getNumberOfPages()).toBe(1);
  });
});
