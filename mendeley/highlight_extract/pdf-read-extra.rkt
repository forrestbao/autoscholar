#lang racket
(require pdf-read/ffi)
(require ffi/unsafe)

(provide page-attr-in-rect page-attr)

(define-cstruct _PopplerColor
  ([red _uint16]
   [green _uint16]
   [blue _uint16]))
(define-cstruct _PopplerTextAttributes
  ([font-name _string]
   [font-size _double]
   [is-underlined _bool]
   [color _PopplerColor]
   [start-index _int]
   [end-index _int]))

(define-poppler page-attr-in-rect
  (_fun (maybe-page x1 y1 x2 y2) ::
        [page-ptr : _PopplerPagePointer = (to-page maybe-page)]
        [rect : (_ptr i _PopplerRectangle)
              = (make-PopplerRectangle x1 y1 x2 y2)]
        -> [rglist : _GListPtr]
        -> (map PopplerTextAttributes->list
                (glist->list/free! rglist _PopplerTextAttributes)))
  #:c-id poppler_page_get_text_attributes_for_area)

(define-poppler page-attr
  (_fun (maybe-page) ::
        [page-ptr : _PopplerPagePointer = (to-page maybe-page)]
        -> [rglist : _GListPtr]
        -> (map PopplerTextAttributes->list
                (glist->list/free! rglist _PopplerTextAttributes)))
  #:c-id poppler_page_get_text_attributes)
