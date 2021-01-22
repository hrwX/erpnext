export const Sortable = ($container) => {

}

export const Draggable = ($container, $element, $handle) => {
  let isMouseDown = false;

  $handle.on('mousedown', () => {
    isMouseDown = true;
  });

  $(window).on('mousemove', () => {
    if ( isMouseDown ) {
      
    }
  });

  $(window).on('mouseup', () => {
    isMouseDown = false;
  });
}