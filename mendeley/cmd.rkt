#lang racket

(require "main.rkt")

(require db)

(define cmd-list (make-parameter #f))
(define cmd-html (make-parameter #f))
(define cmd-group-name (make-parameter ""))

(define db-file
  (command-line
   #:program "pdfhl"
   #:once-each
   [("-l" "--list") "List available group names"
                    (cmd-list #t)]
   [("-g" "--group") group "Group name"
                     (cmd-group-name group)]
   #:once-any
   [("--html") "html"
                    (cmd-html #t)]
   #:args (db-file) db-file))

(define conn
  (sqlite3-connect #:database (expand-user-path db-file)
                   #:mode 'read-only))

(if (cmd-list)
    (displayln
     (string-join (get-group-names conn) (string #\newline)))
    (if (non-empty-string? (cmd-group-name))
        (let ([ids (get-group-document-ids
                    conn (cmd-group-name))])
          (for ([id ids])
            (let ([f (get-document-file conn id)])
              (when (non-empty-string? f)
                (display-to-file
                 f (~a id "-pdf-path.txt")
                 #:exists 'replace)
                (if (cmd-html)
                    (begin
                      (displayln (~a "Generating " id ".html .."))
                      (display-to-file
                       (mendeley-document->html conn id)
                       (~a id ".html")
                       #:exists 'replace))
                    (begin
                      (displayln (~a "Generating " id "-hl.txt and "
                                     id  " -full.txt .."))
                      (display-to-file
                       (get-highlight-text conn id)
                       (~a id "-hl.txt")
                       #:exists 'replace)
                      (display-to-file
                       (get-document-text conn id)
                       (~a id "-full.txt")
                       #:exists 'replace)))))))
        (println "Invalid command. use --help to see available
options")))
