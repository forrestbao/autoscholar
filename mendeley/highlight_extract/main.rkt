#lang racket


(require db)
(require pict pdf-read)
(require rackunit)
(require racket/cmdline)
(require net/url)
(require net/mime)
(require libuuid)
(require "pdf-read-extra.rkt")


(provide get-group-names
         get-group-document-ids
         get-document-title
         get-document-file
         get-highlight-spec
         mendeley-document->html
         get-highlight-text
         get-document-text
         mendeley-group->txt
         mendeley-group->html
         is-bold-font?
         is-italic-font?
         db-annotate-document
         remove-auto-annotate)

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
(define (get-document-title conn id)
  (query-value conn (~a "select title from Documents where id=\"" id "\"")))

;; (get-group-document-ids conn "nsf")
;; (get-document-title conn 22)

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
          (let ([str (vector-ref (first query-result) 0)])
            (if (non-empty-string? str)
                (substring str
                           (string-length "file://"))
                ""))))))

(define (db-get-doi conn id)
  (let ([query (~a "SELECT doi FROM Documents where id=" id)])
    (query-value conn query)))

(module+ test
  (define ids (get-group-document-ids conn "NSF project"))
  (define dois (for/list ([id ids])
                 (db-get-doi conn id)))

  (display-to-file (string-join dois "\n")
                   "dois.txt"
                   #:exists 'replace))

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

;; this is exactly the same as reverse
(define (pdf-read-rect->mendeley-rect pdf rect)
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
                     ;; remove records that contains sql-null
                     (map vector->list (query-rows conn query)))))))

;; FIXME change format of the coordinates
(define (insert-highlight conn id rects)
  (let ([page (pdf-page  (get-document-file conn id) 0)]
        [pagenum (first rects)])
    (for ([rect (second rects)])
      (match-let ([(list x1 y1 x2 y2)
                   (pdf-read-rect->mendeley-rect page rect)])
        (let ([q (λ (s)
                   (~a "\"" s "\""))])
          (let* ([uuid (uuid-generate)]
                 [sql-file-highlights
                  (~a "insert into FileHighlights "
                      "(author, uuid, documentId, fileHash, createdTime,unlinked,color)"
                      " values ("
                      (q "Auto Scholar") ","
                      (q uuid) "," (q (number->string id)) ","
                      (q (get-document-hash conn id)) ","
                      (q "2017-06-10T18:45:53Z") "," (q "false")
                      "," (q "#fff5ad") ")")]
                 [sql-hlid (~a "select id from FileHighlights where uuid = " (q uuid))])
            ;; (displayln "executing ..")
            ;; (displayln sql-file-highlights)
            (query-exec conn sql-file-highlights)
            ;; (displayln "querying highlight ID ..")
            (let ([hlid (query-value conn sql-hlid)])
              ;; (displayln (~a "highlight ID: " hlid))
              (let ([sql-file-highlight-rects
                     (~a "insert into FileHighlightRects "
                         "(highlightId, page, x1, y1, x2, y2)"
                         " values "
                         "(" (q hlid) "," (number->string pagenum)
                         "," x1 "," y1 "," x2 "," y2 ")")])
                ;; (displayln "executing ..")
                ;; (displayln sql-file-highlight-rects)
                (query-exec conn sql-file-highlight-rects)
                ;; (displayln "done!")
                ))))))) )

(define (remove-auto-annotate conn)
  ;; 1. select uuid from filehighlights where author=AutoScholar
  ;; 2. delete from filehighlightrects where uuid=uuid
  ;; 3. delete from filehighlights where author=AutoScholar
  (let ([q (~a "select uuid from FileHighlights where author=\"Auto Scholar\"")])
    (for ([uuid (query-list conn q)])
      (let ([dq1 (~a "delete from FileHighlightRects where id=\"" uuid "\"")]
            [dq2 (~a "delete from FileHighlights where author=\"Auto Scholar\"")])
        (query-exec conn dq1)
        (query-exec conn dq2)))))

;; (get-highlight-spec conn 67)

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

;; (visualize-highlight conn 48)

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
  (apply string-append
         (let ([text (page-text page)])
           (for/list ([i (in-naturals)]
                      [letter (in-string text)])
             (~a (segment-prefix i segments)
                 (string-replace (string letter)
                                 "\n" "</br>\n")
                 (segment-suffix i segments))))))

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


(define bold-fonts '("AdvPTimesB" "AdvPTimesBI"))
(define italic-fonts '("AdvPTimesI" "AdvPTimesBI"))

(define (is-bold-font? font-name)
  (or (string-contains? font-name "bold")
      (string-contains? font-name "Bold")
      (regexp-match? #rx".*[\\._-][bB]$" font-name)
      (regexp-match? #rx".*[\\._-][bB][iI]$" font-name)
      (regexp-match? #rx".*Bd(It)?$" font-name)
      (member font-name bold-fonts)))
(define (is-italic-font? font-name)
  (or (string-contains? font-name "italic")
      (string-contains? font-name "Italic")
      (regexp-match? #rx".*[\\._-][iI]$" font-name)
      (regexp-match? #rx".*[\\._-][bB][iI]$" font-name)
      (regexp-match? #rx".*It$" font-name)
      (regexp-match? #rx".*(Bd)?It$" font-name)
      (member font-name italic-fonts)))

(define (attr->index-segments attr func)
  (map (λ (v)
         (take-right v 2))
       (filter (λ (v)
                 (func (first v)))
               attr)))


(define (mendeley-group-list-fonts conn group-name)
  "list the fonts used in group"
  (let ([ids (get-group-document-ids
              conn group-name)])
    (remove-duplicates
     (apply append
            (for/list ([id ids])
              (let ([f (get-document-file conn id)])
                (when (non-empty-string? f)
                  (let ([pagenum (pdf-count-pages f)])
                    (remove-duplicates
                     (apply append
                            (for/list ([i (in-range pagenum)])
                              (remove-duplicates (map first (page-attr (pdf-page f i)))))))))))))))

(module+ test
  (page-attr (pdf-page (get-document-file conn 49) 0))
  (is-italic-font? "sdfjjsdf-i")
  (mendeley-group-list-fonts conn "NSF project")
  )

(define (get-subscript-segments attr)
  "Heuristic:
1. assume only subscript
2. the font size should be less
3. the length of the subscript must be less than 5
"
  (for/fold ([prev-size (second (first attr))]
             [segments '()]
             #:result segments)
            ([current (in-list (rest attr))])
    (let ([current-size (second current)])
      (if (and (< current-size prev-size)
               (< (apply - (reverse (take-right current 2))) 5))
          (values current-size
                  (append segments (list (take-right current 2))))
          (values current-size segments)))))


(module+ test
  (get-subscript-segments (page-attr (pdf-page (get-document-file conn 60) 2)))
  )

(define (sort-merge-segments segs)
  "Sort and Merge segments if their gaps are within 5"
  (let ([res '()])
    (let ([x (foldl (λ (v acc)
                      ;; (println "------")
                      ;; (println v)
                      ;; (println acc)
                      (if acc
                          (if (< (- (first v) (second acc)) 5)
                              (list (first acc)
                                    (max (second v) (second acc)))
                              (begin
                                (set! res (append res (list acc)))
                                v))
                          v))
                    #f
                    (sort segs < #:key first))])
      (if x
          (append res (list x))
          res))))

(module+ test
  (sort-merge-segments '((1 3) (20 30) (4 5) (9 10)))
  )

(define (mendeley-document->html conn id)
  (let* ([f (get-document-file conn id)])
    (if (not (non-empty-string? f))
        (displayln (~a "No pdf file downloaded for " id))
        (let ([pagenum (pdf-count-pages f)]
              [hls (apply append (get-highlight-spec conn id))])
          (string-append
           "<html>\n"
           "<meta charset=\"UTF-8\">\n"
           "<head> <style> hl { background-color: yellow; } </style> </head>\n"
           "<body>\n"
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
                                      (page-attr page) is-bold-font?)]
                      [italic-segments (attr->index-segments
                                        (page-attr page) is-italic-font?)]
                      [subscript-segments (get-subscript-segments (page-attr page))])
                  ;; (println "--------")
                  ;; (println (sort-merge-segments hl-segments))
                  (page->html page
                              (list (list
                                     (sort-merge-segments
                                      hl-segments) "hl")
                                    ;; retain only <hl> to form valid htmls
                                    ;; (list bold-segments "b")
                                    ;; (list italic-segments "i")
                                    ;; (list subscript-segments "sub")
                                    ))))))
           "</body>" "</html>")))))

(define (mendeley-group->html conn group-name)
  (let ([ids (get-group-document-ids
              conn group-name)])
    (for ([id ids])
      (let ([f (get-document-file conn id)])
        (when (non-empty-string? f)
          (display-to-file
           f (~a id "-pdf-path.txt")
           #:exists 'replace)
          (displayln (~a "Generating " id ".html .."))
          (display-to-file
           (mendeley-document->html conn id)
           (~a id ".html")
           #:exists 'replace))))))

(define (mendeley-group->txt conn group-name)
  (let ([ids (get-group-document-ids
              conn group-name)])
    (for ([id ids])
      (let ([f (get-document-file conn id)])
        (when (non-empty-string? f)
          (display-to-file
           f (~a id "-pdf-path.txt")
           #:exists 'replace)
          (displayln (~a "Generating " id "-hl.txt and "
                         id  " -full.txt .."))
          (display-to-file
           (get-highlight-text conn id)
           (~a id "-hl.txt")
           #:exists 'replace)
          (display-to-file
           (get-document-text conn id)
           (~a id "-full.txt")
           #:exists 'replace))))))


(module+ test
  (define conn
    (sqlite3-connect #:database "/home/hebi/.local/share/data/Mendeley Ltd./Mendeley Desktop/lihebi.com@gmail.com@www.mendeley.com.sqlite"))

  ;; (query-rows conn "select * from Groups")
  ;; (query-rows conn "select * from FileHighlights")

  (define dirichlet-pdf (pdf-page "/home/hebi/.local/share/data/Mendeley%20Ltd./Mendeley%20Desktop/Downloaded/Blei,%20Ng,%20Jordan%20-%202012%20-%20Latent%20Dirichlet%20Allocation.pdf" 0))
  (define first-page-spec (first (get-highlight-spec 38)))

  (get-highlight-text conn 48)

  (get-group-names conn)
  (get-group-document-ids conn "NSF project")
  (mendeley-group->txt conn "NSF project")
  (mendeley-group->html conn "NSF project")


  
  (length (page-text-layout (pdf-page pdf-file 0)))
  (string-length (page-text (pdf-page pdf-file 0)))

  (display-to-file
   (mendeley-document->html conn 48)
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

(define (align-sentence text pattern)
  ;; call agrep
  ;; PARAM: edit distance
  ;; return: '(cost start end)
  ;; remove brackets in pattern
  (let ([p (regexp-replace* #rx"[][()]+" pattern "")])
    (let ([cmd (~a "agrep -E 100 -d fjdsilfadsj --show-position --show-cost "
                   "\"" p "\"")])
      ;; (displayln (~a "-- " cmd))
      (match-let ([(list stdout stdin pid stderr proc)
                   (process cmd)])
        (write-string text stdin)
        (close-output-port stdin)
        ;; (displayln "-- waiting")
        (proc 'wait)
        ;; (displayln "-- done")
        (let ([output (port->string stdout)])
          (let ([match-result (regexp-match #px"([0-9]+):([0-9]+)-([0-9]+):"
                                            ;; "38-91:f"
                                            output)])
            (if (not match-result) #f
                (begin
                  (map string->number (rest match-result))))))))))

(module+ test
  (align-sentence "helccliio world" "hello")
  (align-sentence "hedjifllo world \nhellioo hello" "hello")
  (process "ls")
  )

(define (boxes->rects boxes)
  ;; merge boxes into rects according to their line position. What
  ;; about the 1. on different page (or different columns) 2. line
  ;; position does not match preciesly
  ;;
  ;; remove if x1 and x2 are same
  (for/list ([group (group-by second (filter-not (λ (b)
                                                   (= (first b) (third b)))
                                                 boxes)
                              (λ (x y)
                                (< (abs (- x y)) 0.5)))])
    (let ([x1 (apply min (map first group))]
          [y1 (apply min (map second group))]
          [x2 (apply max (map third group))]
          [y2 (apply max (map fourth group))])
      (list x1 y1 x2 y2))))

(define (annotate-sentence pdf-file sentence)
  ;; get text and bounding box. this only support one alignment,
  ;; because the interface of agrep. The python interface also
  ;; supports only one match output.
  ;;
  ;; I'm going to do this once for each page, and highlight the best
  ;; one
  ;;
  ;; page number start from 1
  ;;
  ;; Return: '((pagenum ((x1, y1, x2, y2) ...)))
  (let ([lst (filter-not
              void?
              (for/list ([i (pdf-count-pages pdf-file)])
                (let* ([page (pdf-page pdf-file i)]
                       [text (page-text page)]
                       [boxes (page-text-layout page)])
                  ;; align sentence in the text
                  (let ([index (align-sentence text sentence)])
                    (when index
                      (let ([cost (first index)]
                            [start (second index)]
                            [end (third index)])
                        ;; get the bounding boxes of the alignment
                        (let ([marked-boxes (take (drop boxes start)
                                                  (- end start))])
                          ;; merge alignments into rectangles according to their boxes
                          (let ([rects (boxes->rects marked-boxes)])
                            (list cost (add1 i) rects)))))))))])
    (if (empty? lst) (list)
        (begin
          (list (rest
                (argmin
                 (λ (x) (first x))
                 lst)))))))

(define (db-annotate-document conn id sentence)
  (let ([pdf-file (get-document-file conn id)])
    (for ([rect (annotate-sentence pdf-file sentence)])
      ;; insert highlight into mendeley database
      (displayln "inserting highlight ..")
      (insert-highlight conn id rect))))


(module+ test
  #;
  (define conn
    (sqlite3-connect #:database "/home/hebi/.local/share/data/Mendeley Ltd./Mendeley Desktop/lihebi.com@gmail.com@www.mendeley.com.sqlite"))

  (get-group-document-ids conn "test")
  (define pdf-file (get-document-file conn 82))
  (page->pict (pdf-page pdf-file 0))
  (page-text (pdf-page pdf-file 0))
  (take (page-text-layout (pdf-page pdf-file 0)) 10)
  (get-highlight-spec conn 82)

  ;; annotate
  (db-annotate-document conn 82
                        ;; "formulas in finite first-order logic"
                        "combine a logical language (e.g., Prolog, description")
  
  (remove-auto-annotate conn)

  ;; TODO close db
  ;; TODO multiple page

  (insert-highlight
   conn 82
   '(2 ((336.94002000000023 254.79452064 541.2986349600002 266.79950184))))

  
  )
