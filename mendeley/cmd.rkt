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
        (if (cmd-html)
            (mendeley-group->html conn (cmd-group-name))
            (mendeley-group->txt conn (cmd-group-name)))
        (println "Invalid command. use --help to see available
options")))
