#lang racket

(require "main.rkt")

(require db)

(define cmd-list (make-parameter #f))
(define cmd-html (make-parameter #f))
(define cmd-list-doc (make-parameter #f))
(define cmd-annotate (make-parameter #f))
(define cmd-remove-annotation (make-parameter #f))
(define cmd-group-name (make-parameter #f))
(define cmd-document-id (make-parameter #f))
(define cmd-pattern (make-parameter #f))

(define db-file
  (command-line
   #:program "pdfhl"
   #:once-any
   [("--list-groups") "List available group names"
                      (cmd-list #t)]
   ;; need to provide group name
   [("--list-documents") "List documents ID and their titles"
                         (cmd-list-doc #t)]
   ;; need to provide document id
   [("--annotate") "Annotate sentence to document"
                   (cmd-annotate #t)]
   [("--remove-annotation") "Remove annotations made by Auto Scholar"
                            (cmd-remove-annotation #t)]
   #:once-each
   [("-g" "--group") group "Group name"
                     (cmd-group-name group)]
   [("-d" "--document") id "Document Id"
                        (cmd-document-id (string->number id))]
   [("--pattern") pattern "Pattern string to annotate"
                  (cmd-pattern pattern)]
   ;; optional
   [("--html") "html"
                    (cmd-html #t)]
   #:args (db-file) db-file))

(define conn
  (sqlite3-connect #:database (expand-user-path db-file)))

(when (cmd-list)
  (displayln
   (string-join (get-group-names conn) (string #\newline)))
  (exit))

(when (cmd-list-doc)
  (when (cmd-group-name)
    (for ([id (get-group-document-ids conn (cmd-group-name))])
      (displayln (~a id "\t" (get-document-title conn id))))))

(when (cmd-annotate)
  (when (and (cmd-document-id)
             (cmd-pattern))
    (db-annotate-document conn (cmd-document-id) (cmd-pattern))))

(when (cmd-remove-annotation)
  (remove-auto-annotate conn))

(when (non-empty-string? (cmd-group-name))
  (if (cmd-html)
      (mendeley-group->html conn (cmd-group-name))
      (mendeley-group->txt conn (cmd-group-name))))

;; (println "Invalid command. use --help to see available options")
