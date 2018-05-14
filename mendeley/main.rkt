#lang racket


(require db)
(require pict pdf-read)
(require rackunit)
(require racket/cmdline)
(require "pdf-read-extra.rkt")

(provide get-group-names
         get-group-document-ids
         get-document-file
         get-highlight-spec
         mendeley-document->html
         get-highlight-text
         get-document-text)


(define (get-group-document-ids conn group-name)
  (let ([query (~a "SELECT documentId
            FROM RemoteDocuments
JOIN Groups
ON Groups.id=RemoteDocuments.groupId
WHERE Groups.name=\"" group-name "\"")])
    (map first (map vector->list (query-rows conn query)))))

(define (get-group-names conn)
  (let ([query (~a "SELECT name FROM Groups")])
    (filter non-empty-string?
            (apply append
                   (map vector->list (query-rows conn query))))))

;; (get-group-document-ids "nsf")

#;
(filter (λ (id)
          (non-empty-string? (get-document-file-from-id id)))
        (get-group-document-ids "nsf"))


(define (get-document-file conn id)
  "Return file name or empty string"
  (let ([query (~a "SELECT Files.localUrl from Files LEFT JOIN
DocumentFiles ON DocumentFiles.hash=Files.hash where
DocumentFiles.documentId=" id)])
    (let ([query-result (query-rows conn query)])
      (if (empty? query-result) ""
          (substring
           (vector-ref (first query-result) 0)
           (string-length "file://"))))))

(define (get-document-hash conn id)
  (let ([query (~a "SELECT Files.hash from Files LEFT JOIN
DocumentFiles ON DocumentFiles.hash=Files.hash where
DocumentFiles.documentId=" id)])
    (let ([query-result (query-rows conn query)])
      (if (empty? query-result) ""
          (vector-ref (first query-result) 0)))))

;; (get-document-hash-from-id 38)

(define (mendeley-rect->pdf-read-rect pdf rect)
  (match-let ([(list x1 y1 x2 y2) rect])
    (let ([height (second (page-size pdf))])
      (list x1 (- height y2) x2 (- height y1)))))

(define (get-highlight-spec conn id)
  ;; note that there might be multiple id corresponding to the same
  ;; file. The highlights, however, relate to one id. So, using
  ;; document id to get highlights will not get all the highlights
  (let ([query (~a "select FileHighlightRects.page, 
FileHighlightRects.x1, FileHighlightRects.y1,
FileHighlightRects.x2, FileHighlightRects.y2
FROM Files
LEFT JOIN FileHighlights
ON FileHighlights.fileHash=Files.hash
LEFT JOIN FileHighlightRects
ON FileHighlightRects.highlightId=FileHighlights.id
where Files.hash=\"" (get-document-hash conn id) "\"
order by FileHighlightRects.page")])
    (let ([convert (λ (spec)
                     (append (take spec 1)
                             (mendeley-rect->pdf-read-rect
                              (pdf-page (get-document-file conn id) 0)
                              (drop spec 1))))])
      ;; group by pages
      (group-by (λ (v) (first v))
                (map convert
                     (map vector->list (query-rows conn query)))))))

;; (get-highlight-spec 38)


;; 1. sort and partition highlights based on file and page
;; 2. for each page, render a pict, mark all highlight

;; Now, I want to get the whole text, and embed the highlight inside
;; with <hl></hl> tags.

;; Also, I want to get the font name and size.


(define (get-highlight-text conn id)
  (let ([file-hl (get-highlight-spec conn id)]
        [f (get-document-file conn id)])
    (for/list ([page-hl (in-list file-hl)])
      (let* ([p (sub1 (first (first page-hl)))]
             [pdf (pdf-page f p)]
             [view (page->pict pdf)])
        (for/list ([hl (in-list page-hl)])
          (match-let*
              ([(list x1 y1 x2 y2)
                (drop hl 1)])
            (page-text-in-rect pdf 'glyph x1 y1 x2 y2)))))))


;; (get-highlight-text conn 38)

(define (visualize-highlight conn id)
  (let ([file-hl (get-highlight-spec conn id)]
        [f (get-document-file conn id)])
    (for/list ([page-hl (in-list file-hl)])
      (let* ([p (sub1 (first (first page-hl)))]
             [pdf (pdf-page f p)])
        (scale
         (for/fold ([view (page->pict pdf)])
                   ([hl (in-list page-hl)])
           (match-let*
               ([(list x1 y1 x2 y2)
                 (drop hl 1)])
             (pin-over view x1 y1
                       (cellophane
                        (colorize
                         (filled-rectangle (- x2 x1) (- y2 y1))
                         "yellow")
                        0.5))))
         1.5)))))

;; (visualize-highlight conn 38)

(define (add-empty-attr text-with-layout)
  (map (λ (l) (append l '(()))) text-with-layout))

(define (rect-overlap? r1 r2)
  "Check if small is within big"
  (match-let ([(list r1x1 r1y1 r1x2 r1y2) r1]
              [(list r2x1 r2y1 r2x2 r2y2) r2])
    ;; FIXME logic
    (not (or (> r1x1 r2x2)
             (> r2x1 r1x2)
             (> r1y1 r2y2)
             (> r2y1 r1y2)))))
(module+ test
  (rect-overlap? '(1 2 3 4) '(1 3 4 5))
  (rect-overlap? '(1 2 3 4) '(4 5 6 7))
  (rect-overlap? '(1 2 3 4) '(1 3 4 5))

  )

(define (mark-hl attr-text page-hl)
  "Precondition: same page"
  (map (λ (letter)
         (if (empty?
              (filter
               identity
               (map (λ (hl)
                      (rect-overlap? (second letter) hl))
                    page-hl)))
             letter
             (append (drop-right letter 1)
                     (list (append (last letter) '(hl))))))
       attr-text))

(define (filter-hl attr-text)
  (filter (λ (letter)
            (member 'hl (last letter)))
          attr-text))


;; how about getting the index of highlights?

(define (page-hl->index-segments page page-hl)
  ;; 1. get all text
  ;; 2. mark hl
  ;; 3. count start and stop indexes
  (list->segments
   (indexes-where (mark-hl
                   (add-empty-attr
                    (page-text-with-layout page))
                   page-hl)
                  (λ (letter)
                    (member 'hl (last letter))))))

(define (attr->index-segments attr font-name)
  (map (λ (v)
         (take-right v 2))
       (filter (λ (v)
             (string-contains? (first v) font-name))
           attr)))

#;
(define (page-text-not-in-rects page rects)
  "Return the text that is not in rects. Concatenate them.")

;; (page-find-text dirichlet-pdf "deployed in modern Internet ")

(define (list->segments lst)
  "from list of numbers, to segments of (start,end)"
  (if (empty? lst) '()
      (for/fold ([res '()]
                 [start (first lst)]
                 [stop (first lst)]
                 #:result (append res (list (list start stop))))
                ([v (in-list (rest lst))])
        (if (= (+ stop 1) v)
            (values res start v)
            (values
             (append res (list (list start stop)))
             v v)))))

(module+ test
  (list->segments '())
  (check-equal? (list->segments '(1)) '((1 1)))
  (check-equal? (list->segments '(1 2 3 6 7 9 10 11 18 19 20 21))
                '((1 3) (6 7) (9 11) (18 21)))
  )

(define (segment-prefix i segments)
  (apply string-append
         (for/list ([segment segments])
           (let ([segs (first segment)]
                 [tag (second segment)])
             (if (member i (map first segs))
                 (~a "<" tag ">")
                 "")))))

(define (segment-suffix i segments)
  (apply string-append
         (for/list ([segment segments])
           (let ([segs (first segment)]
                 [tag (second segment)])
             (if (member i (map second segs))
                 (~a "</" tag ">")
                 "")))))

(define (page->html page segments)
  (~a "<html>"
      "<head> <style> hl { background-color: yellow; } </style> </head>"
      "<body>"
      (apply string-append
             (let ([text (page-text page)])
               (for/list ([i (in-naturals)]
                          [letter (in-string text)])
                 (~a (segment-prefix i segments)
                     (string-replace (string letter)
                                     "\n" "</br>\n")
                     (segment-suffix i segments)))))
      "</body>" "</html>"))

(define (get-document-text conn id)
  (let ([f (get-document-file conn id)])
    (if (not (non-empty-string? f))
        (displayln (~a "No pdf file downloaded for " id))
        (let ([pagenum (pdf-count-pages f)])
          (apply
           string-append
           (for/list ([i (in-range pagenum)])
             (let ([page (pdf-page f i)])
               (page-text page))))))))


(define (mendeley-document->html conn id)
  (let* ([f (get-document-file conn id)])
    (if (not (non-empty-string? f))
        (displayln (~a "No pdf file downloaded for " id))
        (let ([pagenum (pdf-count-pages f)]
              [hls (apply append (get-highlight-spec conn id))])
          (apply
           string-append
           (for/list ([i (in-range pagenum)])
             (let ([page (pdf-page f i)]
                   [page-hl (filter
                             (λ (page-hl)
                               (= (first page-hl) (add1 i)))
                             hls)])
               (let ([hl-segments (page-hl->index-segments
                                   page
                                   (map (λ (l) (drop l 1)) page-hl))]
                     [bold-segments (attr->index-segments
                                     (page-attr page) "Bold")]
                     [italic-segments (attr->index-segments
                                       (page-attr page) "Italic")])
                 (page->html page
                             (list (list hl-segments "hl")
                                   (list bold-segments "b")
                                   (list italic-segments "i")))))))))))

(module+ test
  (define conn
    (sqlite3-connect #:database "/home/hebi/.local/share/data/Mendeley Ltd./Mendeley Desktop/lihebi.com@gmail.com@www.mendeley.com.sqlite"
                     #:mode 'read-only))

  ;; (query-rows conn "select * from Groups")
  ;; (query-rows conn "select * from FileHighlights")

  (define dirichlet-pdf (pdf-page "/home/hebi/.local/share/data/Mendeley%20Ltd./Mendeley%20Desktop/Downloaded/Blei,%20Ng,%20Jordan%20-%202012%20-%20Latent%20Dirichlet%20Allocation.pdf" 0))
  (define first-page-spec (first (get-highlight-spec 38)))

  (get-highlight-text conn 38)

  (display-to-file
   (mendeley-document->html conn 41)
   "test.html"
   #:exists 'replace)


  ;; get all text with spec by letters on page 0
  ;; mark highlight
  ;; mark font
  ;; output xml (special to bold, italic, hl)
  (filter-hl
   (mark-hl
    (add-empty-attr
     (page-text-with-layout dirichlet-pdf))
    (map (λ (l) (drop l 1)) first-page-spec)))


  (scale (let ([page dirichlet-pdf])
           (for/fold ([pageview (page->pict page)])
                     ([bounding-box
                       (in-list (page-find-text
                                 page
                                 "describe latent"))])
             (match-define (list x1 y1 x2 y2) bounding-box)
             (println (page-text-in-rect dirichlet-pdf 'glyph x1 y1 x2 y2))
             (println
              (page-attr-in-rect dirichlet-pdf x1 y1 x2 y2))
             ;; Each match's bounding box ^
             (pin-over pageview x1 y1
                       (cellophane
                        (colorize (filled-rectangle (- x2 x1) (- y2 y1)) "yellow")
                        0.5)))) 1.5)
  
  )
