import { Component, Input } from '@angular/core';

import { NbDialogService } from '@nebular/theme';

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

  deleteItem(shortcode: string, itemIndex: number) {
    // this.dialogService.open(DialogTemplateComponent)
  }
}
