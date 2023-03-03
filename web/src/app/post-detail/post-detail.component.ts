import { Component, Input, TemplateRef } from '@angular/core';

import { NbDialogService, NbDialogRef } from '@nebular/theme';

import { Post, PostService } from '../services/post.service';

@Component({
  selector: 'post-detail',
  templateUrl: './post-detail.component.html',
  styleUrls: ['./post-detail.component.scss']
})
export class PostDetailComponent {
  @Input() post?: Post
  postService: PostService

  constructor(postService: PostService, private dialogService: NbDialogService) {
    this.postService = postService
  }

  showDeleteItemConfirmation(dialog: TemplateRef<any>, shortcode: string, itemIndex: number) {
    this.dialogService.open(dialog, { context: {shortcode: shortcode, itemIndex: itemIndex} });
  }

  deleteItem(dialogRef: NbDialogRef<TemplateRef<any>>, shortcode: string, itemIndex: number) {
    dialogRef.close()
  }
}
